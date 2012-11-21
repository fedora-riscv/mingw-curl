%?mingw_package_header

Name:           mingw-curl
Version:        7.28.1
Release:        1%{?dist}
Summary:        MinGW Windows port of curl and libcurl

License:        MIT
Group:          Development/Libraries
URL:            http://curl.haxx.se/
Source0:        http://curl.haxx.se/download/curl-%{version}.tar.lzma

BuildArch:      noarch

BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-gettext
BuildRequires:  mingw32-win-iconv
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-libidn
BuildRequires:  mingw32-libssh2
BuildRequires:  mingw32-openssl

BuildRequires:  mingw64-filesystem >= 95
BuildRequires:  mingw64-gcc
BuildRequires:  mingw64-binutils
BuildRequires:  mingw64-gettext
BuildRequires:  mingw64-win-iconv
BuildRequires:  mingw64-zlib
BuildRequires:  mingw64-libidn
BuildRequires:  mingw64-libssh2
BuildRequires:  mingw64-openssl


%description
cURL is a tool for getting files from HTTP, FTP, FILE, LDAP, LDAPS,
DICT, TELNET and TFTP servers, using any of the supported protocols.
cURL is designed to work without user interaction or any kind of
interactivity. cURL offers many useful capabilities, like proxy
support, user authentication, FTP upload, HTTP post, and file transfer
resume.

This is the MinGW cross-compiled Windows library.


# Win32
%package -n mingw32-curl
Summary:        MinGW Windows port of curl and libcurl
Requires:       pkgconfig

%description -n mingw32-curl
cURL is a tool for getting files from HTTP, FTP, FILE, LDAP, LDAPS,
DICT, TELNET and TFTP servers, using any of the supported protocols.
cURL is designed to work without user interaction or any kind of
interactivity. cURL offers many useful capabilities, like proxy
support, user authentication, FTP upload, HTTP post, and file transfer
resume.

This is the MinGW cross-compiled Windows library.

%package -n mingw32-curl-static
Summary:        Static version of the MinGW Windows Curl library
Requires:       mingw32-curl = %{version}-%{release}

%description -n mingw32-curl-static
Static version of the MinGW Windows Curl library.

# Win64
%package -n mingw64-curl
Summary:        MinGW Windows port of curl and libcurl
Requires:       pkgconfig

%description -n mingw64-curl
cURL is a tool for getting files from HTTP, FTP, FILE, LDAP, LDAPS,
DICT, TELNET and TFTP servers, using any of the supported protocols.
cURL is designed to work without user interaction or any kind of
interactivity. cURL offers many useful capabilities, like proxy
support, user authentication, FTP upload, HTTP post, and file transfer
resume.

This is the MinGW cross-compiled Windows library.

%package -n mingw64-curl-static
Summary:        Static version of the MinGW Windows Curl library
Requires:       mingw64-curl = %{version}-%{release}

%description -n mingw64-curl-static
Static version of the MinGW Windows Curl library.


%?mingw_debug_package


%prep
%setup -q -n curl-%{version}


%build
MINGW32_CONFIGURE_ARGS="--with-ca-bundle=%{mingw32_sysconfdir}/pki/tls/certs/ca-bundle.crt"
MINGW64_CONFIGURE_ARGS="--with-ca-bundle=%{mingw64_sysconfdir}/pki/tls/certs/ca-bundle.crt"
%mingw_configure \
  --with-ssl --enable-ipv6 \
  --with-libidn \
  --enable-static --with-libssh2 \
  --without-random

# It's not clear where to set the --with-ca-bundle path.  This is the
# default for CURLOPT_CAINFO.  If this doesn't exist, you'll get an
# error from all https transfers unless the program sets
# CURLOPT_CAINFO to point to the correct ca-bundle.crt file.

# --without-random disables random number collection (eg. from
# /dev/urandom).  There isn't an obvious alternative for Windows:
# Perhaps we can port EGD or use a library such as Yarrow.

# These are the original flags that we'll work towards as
# more of the dependencies get ported to Fedora MinGW.
#
#  --without-ssl --with-nss=%{mingw32_prefix} --enable-ipv6
#  --with-ca-bundle=%{mingw32_sysconfdir}/pki/tls/certs/ca-bundle.crt
#  --with-gssapi=%{mingw32_prefix}/kerberos --with-libidn
#  --enable-ldaps --disable-static --with-libssh2

%mingw_make %{?_smp_mflags}


%install
%mingw_make DESTDIR=$RPM_BUILD_ROOT install

# Remove .la files
find $RPM_BUILD_ROOT -name "*.la" -delete

# Remove the man pages which duplicate documentation in the
# native Fedora package.
rm -r $RPM_BUILD_ROOT%{mingw32_mandir}/man{1,3}
rm -r $RPM_BUILD_ROOT%{mingw64_mandir}/man{1,3}

# Drop the curl.exe tool as end-user binaries aren't allowed in Fedora MinGW
rm -f $RPM_BUILD_ROOT%{mingw32_bindir}/curl.exe
rm -f $RPM_BUILD_ROOT%{mingw64_bindir}/curl.exe


# Win32
%files -n mingw32-curl
%doc COPYING
%{mingw32_bindir}/curl-config
%{mingw32_bindir}/libcurl-4.dll
%{mingw32_libdir}/libcurl.dll.a
%{mingw32_libdir}/pkgconfig/libcurl.pc
%{mingw32_includedir}/curl/

%files -n mingw32-curl-static
%{mingw32_libdir}/libcurl.a

# Win64
%files -n mingw64-curl
%doc COPYING
%{mingw64_bindir}/curl-config
%{mingw64_bindir}/libcurl-4.dll
%{mingw64_libdir}/libcurl.dll.a
%{mingw64_libdir}/pkgconfig/libcurl.pc
%{mingw64_includedir}/curl/

%files -n mingw64-curl-static
%{mingw64_libdir}/libcurl.a


%changelog
* Wed Nov 21 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.28.1-1
- Update to 7.28.1
- Removed all patches as they're not needed for the mingw target

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.25.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Apr 08 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.25.0-1
- Update to 7.25.0
- Added win64 support (contributed by Marc-Andre Lureau)
- Dropped upstreamed patches
- Dropped unneeded RPM tags

* Fri Mar 09 2012 Kalev Lember <kalevlember@gmail.com> - 7.20.1-7
- Remove .la files

* Tue Mar 06 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.20.1-6
- Renamed the source package to mingw-curl (RHBZ #800375)
- Use mingw macros without leading underscore
- Dropped unneeded RPM tags

* Mon Feb 27 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.20.1-5
- Rebuild against the mingw-w64 toolchain
- Let curl use its own errno/WSA error codes
- The function ftruncate64 doesn't need to be reimplemented by curl
  as the mingw-w64 crt already contains an implementation for it

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.20.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Jul 06 2011 Kalev Lember <kalevlember@gmail.com> - 7.20.1-3
- Rebuilt against win-iconv

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.20.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu May 13 2010 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.20.1-1
- Update to 7.20.1
- Merged the patches of the native .spec file (7.20.1-5)
- Dropped the curl.exe
- Use the Win32 threads API instead of mingw32-pthreads
- Dropped BR: pkgconfig

* Fri Dec 11 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.19.7-1
- Update to 7.19.8
- Merged the patches of the native .spec file (7.19.7-8)
- Use %%global instead of %%define
- Automatically generate debuginfo subpackage

* Sat May  9 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.19.4-2
- Merged the patches of the native .spec file (7.19.4-10)

* Fri Apr  3 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 7.19.4-1
- Update to version 7.19.4
- Fixed %%defattr line
- Added -static subpackage. Applications which want to use this
  static library need to add -DCURL_STATICLIB to the CFLAGS
- Merged the patches of the native .spec file (7.19.4-5)

* Fri Feb 20 2009 Richard W.M. Jones <rjones@redhat.com> - 7.18.2-6
- Rebuild for mingw32-gcc 4.4

* Fri Feb  6 2009 Richard W.M. Jones <rjones@redhat.com> - 7.18.2-5
- Include license.

* Fri Feb  6 2009 Richard W.M. Jones <rjones@redhat.com> - 7.18.2-4
- Rebuild against new OpenSSH (because of soname bump).

* Fri Jan 30 2009 Richard W.M. Jones <rjones@redhat.com> - 7.18.2-3
- Requires pkgconfig.

* Thu Nov 13 2008 Richard W.M. Jones <rjones@redhat.com> - 7.18.2-2
- Requires mingw32-filesystem >= 35.

* Thu Nov 13 2008 Richard W.M. Jones <rjones@redhat.com> - 7.18.2-1
- Initial RPM release.
