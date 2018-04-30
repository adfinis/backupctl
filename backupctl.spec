%define __python /usr/bin/python3

Name:           backupctl
Version:        1.1.2
Release:        1%{?dist}
Summary:        Tool to manage zfs volumes and create new dirvish vault configurations.
License:        GPLv3

Source0:        https://github.com/adfinis-sygroup/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python34 python34-setuptools python34-docutils
BuildRoot:      %{_tmppath}/%{name}-%{version}

Requires:       python34-jinja2, python34-setuptools, python34-pyxdg, dirvish, zfs

%description
Tool to manage zfs volumes and create new dirvish vault configurations.

%prep
%setup -q -n %{name}-%{version}

%build
%{__python} setup.py build
rst2man-3.4 backupctl.8.rst > backupctl.8
rst2man-3.4 backupctl.ini.5.rst > backupctl.ini.5
gzip -c backupctl.8 > backupctl.8.gz
gzip -c backupctl.ini.5 > backupctl.ini.5.gz

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
install -Dm0644 %{name}.ini.example %{buildroot}%{_sysconfdir}/%{name}.ini
install -Dm0644 %{name}.8.gz %{buildroot}%{_mandir}/man8/%{name}.8.gz
install -Dm0644 %{name}.ini.5.gz %{buildroot}%{_mandir}/man5/%{name}.ini.5.gz

%clean
rm -rf %{buildroot}

%files
%license COPYING
%doc README.rst
%{python_sitelib}/*
%{_prefix}/bin/backupctl
%config(noreplace)%{_sysconfdir}/%{name}.ini
%{_mandir}/man8/%{name}.8.gz
%{_mandir}/man5/%{name}.ini.5.gz
