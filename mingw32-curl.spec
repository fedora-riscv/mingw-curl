%global __strip %{_mingw32_strip}
%global __objdump %{_mingw32_objdump}
%global _use_internal_dependency_generator 0
%global __find_requires %{_mingw32_findrequires}
%global __find_provides %{_mingw32_findprovides}
%define __debug_install_post %{_mingw32_debug_install_post}

Name:           mingw32-curl
Version:        7.20.1
Release:        1%{?dist}
Summary:        MinGW Windows port of curl and libcurl

License:        MIT
Group:          Development/Libraries
URL:            http://curl.haxx.se/
Source0:        http://curl.haxx.se/download/curl-%{version}.tar.lzma
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

#
# Patches from native Fedora package.
#

# upstream commit e32fe30d0cf7c1f7045ac0bd29322e7fb4feb5c8
Patch0:         curl-7.20.0-e32fe30.patch

# upstream commit d487ade72c5f31703ce097e8460e0225fad80348
Patch1:         curl-7.20.1-d487ade.patch

# upstream commit 82e9b78a388ab539c8784cd853adf6e4a97d52c5
Patch2:         curl-7.20.1-82e9b78.patch

# rhbz #581926
#   upstream commit 2e8b21833a581cc5389833ec4fdeeaa6fb7be538
#   upstream commit 3e759f4fb6018b353bd4a1d608be3a3d7b2c9645
#   upstream commit 016ce4b1daa0f8d44a0da7105e1e1c97531e8b87
Patch3:         curl-7.20.1-crl.patch

# rhbz #581926 - test-case
#   http://curl.haxx.se/mail/lib-2010-04/0214.html
#   (the CA pass phrase used in the patch is 'libcurl')
Patch4:         curl-7.20.1-crl-test.patch

# patch making libcurl multilib ready
Patch101:       curl-7.20.0-multilib.patch

# force -lrt when linking the curl tool and test-cases
#Patch102:       curl-7.20.0-lrt.patch

# prevent configure script from discarding -g in CFLAGS (#496778)
Patch103:       curl-7.19.4-debug.patch

# suppress occasional failure of curl test-suite on s390; caused more likely
# by the test-suite infrastructure than (lib)curl itself
# http://curl.haxx.se/mail/lib-2009-12/0031.html
Patch104:       curl-7.20.1-test-delay.patch

# use localhost6 instead of ip6-localhost in the curl test-suite
Patch105:       curl-7.19.7-localhost6.patch

# experimentally enabled threaded DNS lookup
Patch106:       curl-7.20.1-threaded-dns.patch

# exclude test1112 from the test suite (#565305)
Patch107:       curl-7.20.0-disable-test1112.patch

#
# End of native patches
#

BuildRequires:  automake
BuildRequires:  mingw32-filesystem >= 52
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-gettext
BuildRequires:  mingw32-iconv
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-libidn
BuildRequires:  mingw32-libssh2

# See nss/README for the status of this package.
#BuildRequires:  mingw32-nss
# Temporarily we can use OpenSSL instead of NSS:
BuildRequires:  mingw32-openssl

Requires:       pkgconfig


%description
cURL is a tool for getting files from HTTP, FTP, FILE, LDAP, LDAPS,
DICT, TELNET and TFTP servers, using any of the supported protocols.
cURL is designed to work without user interaction or any kind of
interactivity. cURL offers many useful capabilities, like proxy
support, user authentication, FTP upload, HTTP post, and file transfer
resume.

This is the MinGW cross-compiled Windows library.


%package static
Summary:        Static version of the MinGW Windows Curl library
Requires:       %{name} = %{version}-%{release}
Group:          Development/Libraries

%description static
Static version of the MinGW Windows Curl library.


%{_mingw32_debug_package}


%prep
%setup -q -n curl-%{version}

# Convert docs to UTF-8
# NOTE: we do this _before_ applying of all patches, which are already UTF-8
for f in CHANGES README; do
    iconv -f iso-8859-1 -t utf8 < ${f} > ${f}.utf8
    mv -f ${f}.utf8 ${f}
done

# revert an upstream commit which breaks Fedora builds
%patch0 -p1 -R

# upstream patches (already applied)
%patch1 -p1
%patch2 -p1
%patch3 -p1

# upstream patches (not yet applied)
%patch4 -p1

# Fedora patches
%patch101 -p1
#%patch102 -p1
%patch103 -p1
%patch104 -p1
%patch105 -p1
%patch106 -p1

# exclude test1112 from the test suite (#565305)
%patch107 -p1
rm -f tests/data/test1112

autoreconf

# replace hard wired port numbers in the test suite
sed -i s/899\\\([0-9]\\\)/%{?__isa_bits}9\\1/ tests/data/test*

%build
%{_mingw32_configure} \
  --with-ssl --enable-ipv6 \
  --with-ca-bundle=%{_mingw32_sysconfdir}/pki/tls/certs/ca-bundle.crt \
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
#  --without-ssl --with-nss=%{_mingw32_prefix} --enable-ipv6
#  --with-ca-bundle=%{_mingw32_sysconfdir}/pki/tls/certs/ca-bundle.crt
#  --with-gssapi=%{_mingw32_prefix}/kerberos --with-libidn
#  --enable-ldaps --disable-static --with-libssh2

# The ./configure scripts lacks a check for Win32 threads
# As this breaks compilation of async DNS resolving we add a small hack here
echo "#define USE_THREADS_WIN32 1" >> lib/curl_config.h

# Prevent a possible conflict when mingw32-pthreads is installed
sed -i s/'#define USE_THREADS_POSIX 1'// lib/curl_config.h

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

# Remove the man pages which duplicate documentation in the
# native Fedora package.
rm -r $RPM_BUILD_ROOT%{_mingw32_mandir}/man{1,3}

# Drop the curl.exe tool as end-user binaries aren't allowed in Fedora MinGW
rm -f $RPM_BUILD_ROOT%{_mingw32_bindir}/curl.exe


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING
%{_mingw32_bindir}/curl-config
%{_mingw32_bindir}/libcurl-4.dll
%{_mingw32_libdir}/libcurl.dll.a
%{_mingw32_libdir}/libcurl.la
%{_mingw32_libdir}/pkgconfig/libcurl.pc
%{_mingw32_includedir}/curl/


%files static
%defattr(-,root,root,-)
%{_mingw32_libdir}/libcurl.a


%changelog
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
