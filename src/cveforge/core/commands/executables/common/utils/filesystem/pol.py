import struct
from pathlib import Path
from typing import Annotated, Any, Literal

from rich.markdown import Markdown
from rich.table import Column, Table
import typer

from cveforge.core.context import Context



def pol_reader(context: Context, file: Annotated[Path, typer.Argument]):
    """
    Reader for windows POL files as per described in:
    https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/registry-policy-file-format
    """
    file = file.absolute()
    if not file.exists():
        return None
    data = None
    with file.open("rb") as pol_file:
        data = pol_file.read()
    if not data:
        return None
    header = data[:8]
    signature = header[:4].decode("UTF-8")  # The first 4 bytes is the signature
    version = struct.unpack("<I", header[4:])[
        0
    ]  # The seconds for byte is an integer or DWORD version
    body = data[8:]

    walk_props: dict[str, Any] = {
        "opened": 0,
        "row_index": 0,
        "column_index": 0,
        "column_keys": (
            "key",
            "value",
            "type",
            "size",
            "data",
        ),
        "rows": {},
    }
    i: int = -1
    while True:
        i += 1  # starts in 0 because -1 + 1 is 0
        if len(body) <= i:
            break
        c = body[i]
        if c == b"["[0]:
            walk_props["opened"] += 1
            walk_props["column_index"] = 0
            continue  # Dont add opened [ to the row as is not actual part of the data but a metadata instead
        elif c == b";"[0]:
            walk_props["column_index"] = (walk_props["column_index"] + 1) % len(
                walk_props["column_keys"]
            )  # goes from 0 to column keys length
            continue
        elif c == b"]"[0]:
            # We dont have to worry here for data containing the ] char because we directly added data by using the size and we aren't
            # processing data mannually
            walk_props["opened"] -= 1
            walk_props["row_index"] += 1
            continue
        if not walk_props["opened"]:
            continue
        current_update = {}
        column_key: Literal[
            "key",
            "value",
            "type",
            "size",
            "data",
        ] = walk_props[
            "column_keys"
        ][walk_props["column_index"]]

        if column_key == "data":
            # it means we already have the size retrieved lets figure it out and fetch all the needed data at once
            int_byte: bytes = (
                walk_props["rows"].get(walk_props["row_index"], {}).get("size", b"")
            )
            # FIXME This part of the code is prone to error as what I am going to do is a hack without understanding why this does work
            # the idea was to convert the current size of the size payload which is 5 into a normal DWORD or integer payload which is
            # 4 bytes long, so for it we are just stripping the first byte shamelessly :-) also we tested if the first byte was a sign
            # byte or something but we had no luck, neither changing the endianess or anything

            int_size = int.from_bytes(int_byte[1:], "little")  # 972
            walk_props["rows"][walk_props["row_index"]][
                "size"
            ] = int_size  # update size to be an integer so is only one place that needs to be updated
            if not int_size:
                continue
            data = body[i : i + int_size]
            current_update[column_key] = data
            i += int_size  # as we already read all the data
        else:
            current_update[column_key] = walk_props["rows"].get(
                walk_props["row_index"], {}
            ).get(column_key, b"") + int.to_bytes(c)

        if walk_props["row_index"] not in walk_props["rows"]:
            walk_props["rows"][walk_props["row_index"]] = {}
        walk_props["rows"][walk_props["row_index"]].update(current_update)

    table = Table(
        Column("index"),
        Column("key"),
        Column("value"),
        Column("type"),
        Column("size"),
        Column("data"),
        title=f"{signature} {version}",
    )
    for index, row in enumerate(walk_props["rows"].values()):
        table.add_row(
            str(index + 1),
            row.get("key").decode(),
            row.get("value").decode(),
            row.get("type").decode(),
            str(row.get("size")),
            (
                Markdown(
                    f"[Download file]NOT_IMPLEMENTED_YET{index + 1})"
                )
                if row.get("size")
                else "no data"
            ),
        )
    return table
