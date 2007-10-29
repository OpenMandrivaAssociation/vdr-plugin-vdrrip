
%define plugin	vdrrip
%define name	vdr-plugin-%plugin
%define version	0.3.0
%define rel	2

%bcond_with	plf

%if %with plf
%define distsuffix plf
%endif

Summary:	VDR plugin: A MPlayer using movie encoder
Name:		%name
Version:	%version
Release:	%mkrel %rel
Group:		Video
License:	GPL
# an interesting use of a domain...
URL:		http://www.a-land.de/
Source:		http://www.a-land.de/vdr-%plugin-%version.tgz
# e-tobi script
Source1:	vdrripsplit.sh
# initscript
Source2:	vdrrip.init
Source3:	vdrrip.sysconfig
Patch0:		vdrrip-0.3.0-paths.patch
# (anssi) This seems to be the easiest way to do detaching...
Patch8:		vdrrip-0.3.0-queue-bg.patch
# e-tobi patches
Patch1:		02_maketempdir.dpatch
Patch2:		03_greppid2.dpatch
Patch3:		05_fix-dvdparameter.dpatch
Patch4:		06_fix-ogm-ac3-vdrsync-dev.dpatch
Patch5:		07_preserve-queue-owner.dpatch
Patch6:		11_fix-identify-aspect.dpatch
Patch7:		91_vdrrip+dvd-0.3.0-1.3.7.dpatch
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildRequires:	vdr-devel >= 1.4.1-6
%if %with plf
BuildRequires:	libdvdnav-devel
%endif
Requires:	vdr-abi = %vdr_abi
# The plugin really requires these itself as well
Requires:	mplayer
Requires:	mencoder

%description
Vdrrip is a plugin to encode the vdr recordings into several
formats. You likely want to also install the vdrrip package which
contains the queue handler script.
%if %with plf
This package is in PLF because this build contains support for DVD
ripping which may be prohibited by local laws.
%endif

%package -n %plugin
Summary:	Queue handler of vdrrip
Group:		Video
Requires(preun): rpm-helper
Requires(post):	rpm-helper
Requires:	mplayer
Requires:	mencoder

%description -n %plugin
The queue handler for VDR vdrrip plugin. It does the actual
encoding.

For encoding ogm files you also need the packages ogmtools and
vdrsync. For encoding matroska files you need the packages
mkvtoolnix and vdrsync. For encoding ogm or matroska files with mp3
or ogg vorbis audio you also need the package ffmpeg.

%prep
%setup -q -n %plugin-%version
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
chmod -x TODO COPYING README FAQ HISTORY
perl -pi -e 's,scriptdir=.*$,scriptdir="%{_sysconfdir}/%{plugin}",' scripts/queuehandler.sh
grep scriptdir= scripts/queuehandler.sh

cat > README.install.urpmi <<EOF
You likely want to also install the vdrrip package which
contains the queue handler script.
EOF

%vdr_plugin_params_begin %plugin
# You likely want to also install the vdrrip package which
# contains the queue handler script which does the actual encoding.
#
# use alternative mplayer instead of the default one
var=MPLAYER
param="-p MPLAYER"
# use alternative mencoder instead of the default one
var=MENCODER
param="-e MENCODER"
%if %with plf
# use alternative DVD device instead of /dev/dvd
var=DVD_DEVICE
param="-d DVD_DEVICE"
%endif
%vdr_plugin_params_end

%build
%vdr_plugin_build \
%if %with plf
	VDRRIP_DVD=1
%endif

%install
rm -rf %{buildroot}
%vdr_plugin_install
install -d -m755 %{buildroot}%{_bindir}
install -m755 scripts/queuehandler.sh %{buildroot}%{_bindir}
install -m755 %SOURCE1 %{buildroot}%{_bindir}
install -d -m755 %{buildroot}%{_sysconfdir}/%{plugin}
install -m644 scripts/queuehandler.sh.conf %{buildroot}%{_sysconfdir}/%{plugin}

install -d -m755 %{buildroot}%{_initrddir} %{buildroot}%{_sysconfdir}/sysconfig
install -m755 %SOURCE2 %{buildroot}%{_initrddir}/%{plugin}
install -m644 %SOURCE3 %{buildroot}%{_sysconfdir}/sysconfig/%{plugin}

%clean
rm -rf %{buildroot}

%post
%vdr_plugin_post %plugin

%post -n %plugin
%_post_service %plugin

%preun -n %plugin
%_preun_service %plugin

%postun
%vdr_plugin_postun %plugin

%files -f %plugin.vdr
%defattr(-,root,root)
%doc README HISTORY FAQ TODO COPYING scripts/sleephalt.sh scripts/vdrshutdown.sh

%files -n %plugin
%{_bindir}/vdrripsplit.sh
%{_bindir}/queuehandler.sh
%dir %{_sysconfdir}/%{plugin}
%config(noreplace) %{_sysconfdir}/%{plugin}/queuehandler.sh.conf
%{_initrddir}/%{plugin}
%config(noreplace) %{_sysconfdir}/sysconfig/%{plugin}