# disable tests by default,
# causes failure (perhaps due to resource usage)
# on RPM Fusion build servers (though they work locally)
%bcond_with check

Name:           miro
Version:        5.0.2
Release:        2%{?dist}
Summary:        Internet TV Player

Group:          Applications/Multimedia
# miro-segmenter is GPLv2 only
License:        GPLv2+ and GPLv2
URL:            http://www.getmiro.com/
Source0:        http://ftp.osuosl.org/pub/pculture.org/miro/src/miro-%{version}.tar.gz
# explains video conversion issues
# Source1:        README.Fedora
# handle non-existent iTunes path exception
# submitted: http://bugzilla.pculture.org/show_bug.cgi?id=17925
Patch0:         miro-4.0.2-fix_itunes_path.patch
# fix desktop file
# submitted: http://bugzilla.pculture.org/show_bug.cgi?id=17926
Patch1:         miro-4.0.2-fix_desktop_file.patch
# fix GNOME screensaver not being inhibitable
# submitted: http://bugzilla.pculture.org/show_bug.cgi?id=18018
Patch2:         miro-4.0.2.1-fix_screensaver_inhibit.patch
# Don't install pre-built codegen binaries
Patch3:         miro-5.0.2-no_bundled.patch
# Backport miro-segmenter changes for building with new FFmpeg
Patch4:         miro-5.0.2-fix_ffmpeg.patch

# Miro is temporarily using pre-built codegen binaries
# available only on these two platforms
ExclusiveArch:  i686 x86_64
BuildRequires:  python-devel
BuildRequires:  boost-devel
BuildRequires:  desktop-file-utils
BuildRequires:  ffmpeg-devel
BuildRequires:  gettext
BuildRequires:  Pyrex
BuildRequires:  pygtk2-devel
BuildRequires:  taglib-devel
BuildRequires:  webkitgtk-devel

# for testing
%if %{with check}
BuildRequires:  dbus-x11
BuildRequires:  dbus-python
BuildRequires:  ffmpeg
BuildRequires:  GConf2
BuildRequires:  gnome-python2-gconf
BuildRequires:  gstreamer-plugins-good
BuildRequires:  gstreamer-python
BuildRequires:  python-mutagen
BuildRequires:  python-pycurl
BuildRequires:  pywebkitgtk
BuildRequires:  rb_libtorrent-python
BuildRequires:  Xvfb xauth
%endif

Requires:       avahi-compat-libdns_sd
Requires:       dbus-python
Requires:       dbus-x11
Requires:       ffmpeg
#Requires:       ffmpeg2theora
Requires:       GConf2
Requires:       gnome-python2-gconf
Requires:       gstreamer-plugins-good
Requires:       gstreamer-python
Requires:       python-mutagen
Requires:       python-pycurl
Requires:       pywebkitgtk
Requires:       rb_libtorrent-python

Provides:       Miro = %{version}-%{release}
Obsoletes:      Miro < 3.5.1-2

# we don't want to provide private python extension libs
# http://fedoraproject.org/wiki/Packaging:AutoProvidesAndRequiresFiltering#Arch-specific_extensions_to_scripting_languages
%{?filter_setup:
%filter_provides_in %{python_sitearch}/miro/.*\.so$ 
%filter_setup
}

%description
Miro is a free HD video player.  It offers over 6,000 free internet TV
shows and video podcasts, and has a simple interface designed for
fullscreen HD video. It downloads most videos, allowing users to take
their shows with them.

%prep
%setup -q
# Patches
# Intentionally not using -b .<descr> :
# Otherwise, the unpatched files get re-added into Miro
# (and '.' breaks Python imports)
%patch0 -p2
%patch1 -p2
%patch2 -p2
%patch3 -p1
%if 0%{?fedora} >= 18
%patch4 -p0
%endif
# /Patches


%build
cd linux && CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%check
%if %{with check}
cd linux && LANG=en_US.utf8 xvfb-run -a -w 1 ./test.sh
%endif

%install
cd linux &&  %{__python} setup.py install -O1 --skip-build --root %{buildroot}

desktop-file-validate %{buildroot}%{_datadir}/applications/miro.desktop

# Fix permissions
find %{buildroot}%{_bindir}/miro* -exec chmod 755 '{}' \;
find %{buildroot}%{python_sitearch}/miro -name '*.so' -exec chmod 755 '{}' \;

# Swedish Chef is not a real locale; delete files rather than
# having to own the directory
rm -rf %{buildroot}%{_datadir}/locale/swch
%find_lang miro


%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
update-desktop-database %{_datadir}/applications &> /dev/null ||:
update-mime-database %{_datadir}/mime &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
update-desktop-database %{_datadir}/applications &> /dev/null ||:
update-mime-database %{_datadir}/mime &> /dev/null || :

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -f linux/miro.lang
%{_bindir}/miro*
%{_bindir}/echoprint-codegen
%exclude %{_datadir}/miro/resources/testdata
%{_datadir}/miro
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/pixmaps/*
%{_datadir}/applications/*.desktop
%{_mandir}/man1/*
%{_datadir}/mime/packages/*.xml
%{python_sitearch}/*egg-info
%{python_sitearch}/miro/
%doc README license.txt CREDITS


%changelog
* Wed Sep 26 2012 Michel Salim <salimma@fedoraproject.org> - 5.0.2-2
- Avoid shipping pre-built codegen binary

* Tue Aug  7 2012 Michel Salim <salimma@fedoraproject.org> - 5.0.2-1
- Update to 5.0.2

* Sat May  5 2012 Michel Salim <salimma@fedoraproject.org> - 5.0-2
- Only ship the platform-specific codegen binary

* Fri May  4 2012 Michel Salim <salimma@fedoraproject.org> - 5.0-1
- Update to 5.0

* Fri Mar  2 2012 Michel Salim <salimma@fedoraproject.org> - 4.0.6-3
- Apply upstream patch for terminating DBus after running unit tests
- Disable tests by default; rebuild with --with check to override

* Wed Feb  8 2012 Michel Salim <salimma@fedoraproject.org> - 4.0.6-2
- Add GPLv2 to license field (for miro-segmenter)
- Remove old upgrade path for Democracy package
- Use versioned Obsolete: for the previous Miro package

* Thu Feb  2 2012 Michel Salim <salimma@fedoraproject.org> - 4.0.6-1
- Update to 4.0.6
- Spec clean-ups
- Hide private library from "Provide:" metadata

* Tue Aug  2 2011 Michel Salim <salimma@fedoraproject.org> - 4.0.2.1-4
- Use provided CFLAGS when building miro-segmenter

* Sun Jul 31 2011 Michel Salim <salimma@fedoraproject.org> - 4.0.2.1-3
- Add missing BR for Gstreamer tests

* Sun Jul 31 2011 Michel Salim <salimma@fedoraproject.org> - 4.0.2.1-2
- Fix screensaver inhibition exception when enabling full-screen mode

* Sun Jul 31 2011 Michel Salim <salimma@fedoraproject.org> - 4.0.2.1-1
- Update to 4.0.2.1
- Fix permissions of installed executables and .so modules
- Add missing build and runtime dependencies

* Thu Jul 14 2011 Michel Salim <salimma@fedoraproject.org> - 4.0.2-1
- Update to 4.0.2
- Rename to miro
- Enable unit tests
- Validate desktop entry

* Sat Mar  5 2011 Michel Salim <salimma@fedoraproject.org> - 3.5.1-1
- Update to 3.5.1

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Nov  6 2010 Michel Salim <salimma@fedoraproject.org> - 3.5-2
- Fix positioning of child image to use integer dimensions
- add documentation for video conversion issues

* Sat Nov  6 2010 Michel Salim <salimma@fedoraproject.org> - 3.5-1
- Update to 3.5

* Wed Sep 29 2010 jkeating - 3.0.3-3
- Rebuilt for gcc bug 634757

* Mon Sep 20 2010 Michel Salim <salimma@fedoraproject.org> - 3.0.3-2
- Catch exception when started without a valid DISPLAY (# 633999)

* Sun Aug 29 2010 Alex Lancaster <alexlan[AT]fedoraproject org> - 3.0.3-1
- Update to upstream 3.0.3.  Potentially fixes a whole slew of bugs
  including YouTube downloads not working
  (http://bugzilla.pculture.org/show_bug.cgi?id=14084)

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 3.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu Jun  3 2010 Michel Salim <salimma@fedoraproject.org> - 3.0.2-1
- Update to 3.0.2

* Wed May  5 2010 Michel Salim <salimma@fedoraproject.org> - 3.0.1-1
- Update to 3.0.1

* Mon Apr 12 2010 Martin Stransky <stransky@redhat.com> - 3.0-2
- Updated gecko dependency

* Fri Apr  9 2010 Michel Salim <salimma@fedoraproject.org> - 3.0-1
- Update to 3.0
- Use mimeinfo and icon cache scriptlets
- Drop unneeded dependencies

* Sat Apr 03 2010 Caolán McNamara <caolanm@redhat.com> - 2.5.4-4
- Rebuild against newer gecko

* Tue Mar 23 2010 Jan Horak <jhorak@redhat.com> - 2.5.4-3
- Rebuild against newer gecko

* Fri Jan 22 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 2.5.4-2
- Rebuild for Boost soname bump

* Thu Dec 17 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.5.4-1
- Update to upstream 2.5.4.
- Hopefully fixes a whole slew of crashes (#540301, #540535, #540543)
  (#544047, #545681, #546141, #528036, #540207, #544889, #547062)

* Wed Nov 25 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.5.3-3
- Update to new gecko-libs

* Thu Nov 05 2009 Jan Horak <jhorak@redhat.com> - 2.5.3-2
- Rebuild against newer gecko

* Wed Oct 28 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.5.3-1
- Update to 2.5.3
- Tarball renamed: Miro -> miro

* Tue Oct 27 2009 Jan Horak <jhorak@redhat.com> - 2.5.2-5
- Rebuild against newer gecko

* Fri Sep 11 2009 Jan Horak <jhorak@redhat.com> - 2.5.2-4
- Rebuild against newer gecko

* Thu Aug 06 2009 Jan Horak <jhorak@redhat.com> - 2.5.2-3
- Rebuild against newer gecko

* Tue Aug 04 2009 Jan Horak <jhorak@redhat.com> - 2.5.2-2
- Rebuild against newer gecko

* Tue Aug  4 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.5.2-1
- Update to latest upstream (2.5.2)
- Drop xine hack patch, now upstream
- Rebase remaining patches to 2.5.2 where necessary
- Include new icons in files list

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 19 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.0.5-2
- Rebuild against newer gecko

* Wed Jul  1 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.0.5-1
- Update to latest upstream (2.0.5), fixes #507642

* Sat Jun 13 2009 Alex Lancaster <alexlan[AT}fedoraproject org> - 2.0.4-1
- Update to upstream 2.0.4

* Sat Jun 13 2009 Alex Lancaster <alexlan[AT}fedoraproject org> - 2.0.3-3
- Rebuild against newer Python boost

* Mon Apr 27 2009 Christopher Aillon <caillon@redhat.com> - 2.0.3-2
- Rebuild against newer gecko

* Mon Mar 16 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.0.3-1
- Update to upstream 2.0.3
- Add patch to disable xine-hack, hopefully fixes #480527
- Use internal 0.14 version of rb_libtorrent for < F-11 (#489755)

* Mon Mar  9 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.0.2-1
- Update to upstream 2.0.2
- Add Requires: gstreamer-python (#489134)
- Drop patch for libtorrent 0.13, applied upstream

* Fri Feb 27 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.0-5
- Combine the fhs patches into one, and fix the path to
  /usr/libexec/xine_extractor (#487442)

* Fri Feb 27 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 2.0-4
- Add another upstream patch to fix patch on x86_64 (#487442)

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Michel Salim <salimma@fedoraproject.org> - 2.0-2
- Use system libtorrent >= 0.13
- Do not ship testdata
- Switch default download directory to ~/Videos/Miro

* Tue Feb 10 2009 Michel Salim <salimma@fedoraproject.org> - 2.0-1
- Update to 2.0

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 1.2.8-5
- rebuild with new openssl

* Tue Dec 23 2008 Caolán McNamara <caolanm@redhat.com> - 1.2.8-4
- Rebuild against newer gecko 1.9.1

* Thu Dec 18 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.8-3
- Enable patch for new boost 1.37 for F-11+

* Thu Dec 18 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.8-2
- Rebuild against new boost

* Wed Dec  3 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.8-1
- Update to latest upstream (1.2.8)
- Rebuild for Python 2.6

* Wed Nov 12 2008 Christopher Aillon <caillon@redhat.com> - 1.2.7-2
- Rebuild against newer gecko 1.9.0.4

* Sun Sep 28 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.7-1
- Update to 1.2.7
- Rebuild against gecko-libs 1.9.0.2 (#464205)

* Fri Aug 22 2008 Michel Alexandre Salim <salimma@fedoraproject.org> - 1.2.6-3
- Do not create backup files when patching; the backup files get re-added during the build process

* Fri Aug 22 2008 Michel Salim <salimma@fedoraproject.org> - 1.2.6-2
- Unapply boost patch; boost-1.36 has been backed out for F10

* Fri Aug 22 2008 Michel Salim <salimma@fedoraproject.org> - 1.2.6-1
- Update to 1.2.6
- Patch for boost API change

* Tue Aug 12 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.4-4
- Rebuild for new boost (fixes broken deps).

* Sat Jul 19 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.4-3
- Rebuild for xulrunner-1.9.0.1
- Unfortunately we probably need to make this an exact match because
  Miro uses the unstable API, so a rebuild may need to be done on every
  package update to be sure that it will work with new xulrunner updates

* Wed Jun 18 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.4-2
- Rebuild for xulrunner-1.9 final.

* Sun Jun 15 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.4-1
- Update to latest upstream (1.2.4)

* Mon Apr 28 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.3-2
- Update and re-enable xulrunner patch from Martin Stransky (#393521)

* Mon Apr 28 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.3-1
- Update to official 1.2.3 upstream release (includes the previous
  xulrunner fixes in test release).

* Sat Mar 29 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2.2-0.1.test
- Update to test snapshot which is supposed to fix xulrunner 1.9 support
  (http://bugzilla.pculture.org/show_bug.cgi?id=9692)
- Drop xulrunner patch.

* Fri Mar 28 2008 Christopher Aillon <caillon@redhat.com> - 1.2-2
- Prune spurious (Build)Requires

* Mon Mar 24 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.2-1
- Update to latest upstream (1.2)
- Remove much of xulrunner patch, keep modifications to setup.py to look
  for libxul rather than xulrunner-xpcom

* Tue Mar 11 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.2-4
- Update GCC 4.3 patch by Christopher Aillon (#434480)

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.1.2-3
- Autorebuild for GCC 4.3

* Fri Feb 15 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.2-2
- Patch to build against GCC 4.3.0

* Fri Feb 15 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.2-1
- Update to 1.1.2

* Sat Feb  9 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1-3
- rebuilt for GCC 4.3 as requested by Fedora Release Engineering

* Fri Jan 25 2008 Michel Salim <michel.sylvan@gmail.com> - 1.1-2
- Fix charset mismatch in download window
- Remove shebangs from scripts
- Sanitize end-of-line markers

* Thu Jan 17 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1-1
- Update to upstream 1.1 release
- BuildRequires: gecko-devel-unstable, openssl-devel

* Tue Jan  8 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.0-5
- Update xulrunner patch to use upstream .pc files

* Sun Dec 23 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 1.0-4
- Add support for python eggs for F9+

* Sun Dec 23 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 1.0-3
- Re-enable gecko-libs 1.9, as 1.8.1.10 has now gone away as a BR.
- Add first-cut patch from Martin Stransky from #393521 that attempts to
  patch Miro to work against xulrunner. Likely incomplete. 

* Tue Dec  4 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 1.0-2
- Back to building against 1.8.1.10 (firefox) until #393521 is fixed.

* Fri Nov 16 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 1.0-1
- Update to latest upstream (1.0).

* Wed Nov 14 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.9.9-2
- Build against gecko-libs 1.9 (new xulrunner)

* Fri Nov 09 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.9.9-1
- Update to latest upstream (0.9.9.9)
- Build against gecko-libs 1.8.1.9 (firefox 2.0.0.9)
- Include xine_extractor in package (thanks to Jason Farrell)
- Drop Miro-setup.py.patch

* Thu Nov 01 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.9.1-6
- Update patch with workaround suggested on:
  http://bugzilla.pculture.org/show_bug.cgi?id=8579

* Wed Oct 31 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.9.1-5
- Add setup.py patch to ignore call to svn.

* Tue Oct 30 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.9.1-3
- Add BuildRequires: libXv-devel
- Drop dbus patch

* Sun Oct 28 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.9.1-1
- Update to latest upstream (0.9.9.1)

* Fri Oct 26 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.8.1-8
- Replace Requires and BuildRequires for firefox with gecko to 
  smooth eventual xulrunner transition 

* Thu Oct 25 2007 Alex Lancaster <alexlan[AT]fedoraproject org> 0.9.8.1-7
- Rebuild for new Firefox (2.0.0.8)
- License: GPLv2+ to conform with Fedora licensing guidelines

* Thu Sep 20 2007 Thorsten Scherf <tscherf@redhat.com> 0.9.8.1-3
- new Firefox dep

* Wed Aug 15 2007 Thorsten Scherf <tscherf@redhat.com> 0.9.8.1-2
- made Democracy obsolte with this release

* Tue Aug 14 2007 Thorsten Scherf <tscherf@redhat.com> 0.9.8.1-1
- new upstream version and new naming
- fix to solve the python/dbus problem

* Fri Jun 22 2007 Thorsten Scherf <tscherf@redhat.com> 0.9.6-2
- new upstream version

* Fri Jun 22 2007 Thorsten Scherf <tscherf@redhat.com> 0.9.6-1
- new upstream version

