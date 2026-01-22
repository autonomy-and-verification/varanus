# FDR Troubleshooting

Here are some troubleshooting suggestions for problems with FDR4

## Cannot Install: Depends: libpng12-0 but it is not installable

Using the instructions from: https://www.linuxuprising.com/2018/05/fix-libpng12-0-missing-in-ubuntu-1804.html

```
sudo add-apt-repository ppa:linuxuprising/libpng12
sudo apt update
sudo apt install libpng12-0
```

This solves the problem and allows the installation to continue.

## Cannot run: error while loading shared libraries: libtinfo.so.5: cannot open shared object file: No such file or directory

It seems this can just be installed

```
sudo apt-get install libtinfo5
```

## Cannot run: Could not connect to FDR licensing server; please check your internet connection

This error happens on the License Application dialogue, when trying to validate the license.
Some Linux distributions have moved the TLS certificate store, and FDR cannot find it, so it can't connect. FDR 4.2.7 says it fixes an issue with not being able to connect to the licensing server, but this error still sometimes appears.

The fix that seems to work is to copy the TLS certificates to the location that FDR is expecting them to be at:
```
sudo mkdir -p /etc/pki/tls/certs/
sudo cp /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt
```
