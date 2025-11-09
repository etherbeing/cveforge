#!/usr/bin/python3

import subprocess
import time
import sys
import os

def run_program_with_auto_input(command):
    """
    Runs a program, feeds it a predetermined input string, and captures the result.
    
    Args:
        command (list): The command and its arguments.
    
    Returns:
        int: The exit code of the executed program.
    """
    
    # ----------------------------------------------------------------------
    # The Input String: Three Newlines (for Enter) and Three 'y' inputs.
    # Note: \n might be interpreted as Enter or just a line feed, 
    #       depending on how the target program reads input.
    # ----------------------------------------------------------------------
    # \n = Enter
    # y\n = y + Enter
    input_sequence = "\n" * 4 + "y\n" * 4

    print(f"--- Executing: {' '.join(command)}")
    print("Feeding input: [Enter] x4, [y] x4")

    try:
        # Popen is used to run the command and create pipes for communication
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            text=True  # Handle input/output as text (strings)
        )
        
        # Write the entire input sequence to the subprocess's stdin
        # and close the pipe to signal no more input is coming.
        stdout, _ = process.communicate(input=input_sequence, timeout=30)
        
        # Print the output from the program
        print("\n--- Program Output ---")
        print(stdout.strip())
        print("----------------------")

        # Wait for the process to terminate and get the exit code
        returncode = process.wait()
        return returncode

    except FileNotFoundError:
        print(f"\n❌ Error: Command not found: {command[0]}")
        return 1
    except subprocess.TimeoutExpired:
        print("\n❌ Error: Command timed out. Killing process and retrying.")
        process.kill()
        return 1
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return 1

# ----------------------------------------------------------------------
# Main Retry Loop
# ----------------------------------------------------------------------

if __name__ == "__main__":
    
    # 1. Obtain command from arguments
    if len(sys.argv) < 2:
        print("Usage: python3 script_name.py <program> [arg1] [arg2]...")
        sys.exit(1)
        
    target_command = sys.argv[1:]
    
    attempt = 1
    while True:
        print(f"\n=======================================================")
        print(f"Attempt #{attempt}")
        
        exit_code = run_program_with_auto_input(target_command)
        
        if exit_code == 0:
            print(f"✅ SUCCESS! Program exited with code 0 after {attempt} attempts.")
            print("=======================================================")
            break
        else:
            print(f"❌ FAILURE. Program exited with code {exit_code}. Retrying in 2 seconds...")
            time.sleep(2)
            attempt += 1
