# mothership
Tool to archive RPM packages and attest to their authenticity

# Introduction
This tool is designed to be used by the Rocky Linux project to archive RPM packages and attest to their authenticity.

The sources are first staged, then the fully debranded sources are pushed (Optional).

The import/debrand process is connected to Peridot, while the attestation and archival is fully done by this tool.

# Configuration
```
port: 8080
rekor_endpoint: http://rekor:8090
git_endpoint: ssh://git@git.rockylinux.org:22220/srpm-attest-test
git_ssh_key_path: PATH_TO_SSH_KEY
peridot:
  endpoint: https://peridot-api.build.resf.org
  client_id: CLIENT_ID
  client_secret: CLIENT_SECRET
  project_id: PROJECT_ID
```
