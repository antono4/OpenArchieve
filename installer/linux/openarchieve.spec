Name:           openarchieve
Version:        1.0.0
Release:        1%{?dist}
Summary:        File archiver like WinRAR/WinZip

License:        MIT
URL:            https://github.com/antono4/OpenArchieve
Source0:        OpenArchieve
Source1:        openarchieve.desktop
Source2:        openarchieve.png

BuildArch:      %{_arch}

%global _binaries_in_noarch_packages 1

%description
OpenArchieve is a web-based file archiver that runs as a local desktop app.
It supports creating and extracting ZIP, TAR, TAR.GZ, TAR.BZ2, and TAR.XZ
archives through a WinRAR-style dark UI.

%prep
# nothing to compile

%install
install -D -m 0755 %{SOURCE0} %{buildroot}/opt/OpenArchieve/OpenArchieve
install -D -m 0644 README.md %{buildroot}/opt/OpenArchieve/README.md
install -D -m 0644 icon.png %{buildroot}/opt/OpenArchieve/icon.png
install -D -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/openarchieve.desktop
install -D -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/openarchieve.png
ln -s /opt/OpenArchieve/OpenArchieve %{buildroot}%{_bindir}/openarchieve

%files
/opt/OpenArchieve/
%{_bindir}/openarchieve
%{_datadir}/applications/openarchieve.desktop
%{_datadir}/icons/hicolor/256x256/apps/openarchieve.png

%post
update-desktop-database -q %{_datadir}/applications 2>/dev/null || true
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2>/dev/null || true

%postun
update-desktop-database -q %{_datadir}/applications 2>/dev/null || true
gtk-update-icon-cache -q %{_datadir}/icons/hicolor 2>/dev/null || true

%changelog
* Fri Aug 15 2026 OpenArchieve <openhands@all-hands.dev> - 1.0.0-1
- Initial RPM package
