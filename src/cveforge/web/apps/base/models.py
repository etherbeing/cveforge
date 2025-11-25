from django.db import models

# Create your models here.

class CVEModel(models.Model):
    name = models.CharField()
    year = models.IntegerField()
    cve_id = models.IntegerField()
    summary = models.CharField(default=None)

    def __str__(self):
        return f"CVE_{self.year}_{self.cve_id}: {self.name}"

    #class Meta:
    #    unique_constraints = ("name", "year", "cve_id") # TODO Check if this is the correct syntax

class SoftwareModel(models.Model):
    name = models.CharField()
    version = models.CharField()
    known_vulnerabilities = models.ManyToManyField(CVEModel)
    std_binary_path = models.FilePathField()
    std_tcp_port = models.IntegerField()
    used_tcp_port = models.IntegerField()
    non_categorized_metadata = models.JSONField()

    def __str__(self):
        return self.name
    
class HostModel(models.Model):
    """
    Store info about scanned hosts in the DB
    for example their IPs, their known vulnerabilities, OS version, software versions and more 
    """
    ip_address = models.GenericIPAddressField()
    operative_system_stats = models.ForeignKey(SoftwareModel, on_delete=models.PROTECT, related_name="host_os_set")
    software_stats = models.ManyToManyField(SoftwareModel, related_name="host_software_set")
