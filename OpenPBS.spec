Summary:	Portable Batch System
Summary(pl):	Portable Batch System - przeno¶ny system wsadowy
Name:		OpenPBS
Version:	2.3.16
Release:	0.1
License:	Portable Batch System (PBS) Software License
Group:		Applications/Networking
Source0:	%{name}_2_3_16.tar.gz
# Source0-md5:	42be627d513839a2daf258692b0092aa
Source1:	pbs_mom
Source2:	pbs_server
Source3:	pbs_sched
Source4:	pbsrun
#Source5:	pbsenv.sh
#Source6:	pbsenv.csh
Source7:	pbsconfig
Source8:	patch.ko
URL:		http://www.openpbs.org/
Requires:	tcl
Requires:	tk
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Portable Batch System (PBS) is a flexible batch software
processing system developed at NASA Ames Research Center. It operates
on networked, multi-platform UNIX environments, including
heterogeneous clusters of workstations, supercomputers, and massively
parallel systems.

%description -l pl
PBS (Portable Batch System - przeno¶ny system wsadowy) jest
elastycznym oprogramowaniem do przetwarzania wsadowego rozwijanym w
NASA Ames Research Center. Dzia³a w usieciowionych, wieloplatformowych
¶rodowiskach uniksowych, w³±cznie z heterogenicznymi klastrami stacji
roboczych, superkomputerów i systemów masowego przetwarzania
równoleg³ego.

%package mom
Summary:	PBS client daemon: pbs_mom
Summary(pl):	Demon kliencki PBS: pbs_mom
Group:		Applications/Networking
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}

%description mom
This package contains the PBS client daemon pbs_mom executable and
startup script.

%description mom -l pl
Ten pakiet zawiera demona klienckiego pbs_mom i jego skrypt startowy.

%package server
Summary:	PBS server daemon: pbs_server
Summary(pl):	Demon serwera PBS: pbs_server
Group:		Applications/Networking
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}

%description server
This package contains the PBS server daemon pbs_server executable and
startup script.

%description server -l pl
Ten pakiet zawiera demona serwera PBS (pbs_server) i jego skrypt
startowy.

%package sched
Summary:	PBS scheduler daemon: pbs_sched
Summary(pl):	Demon schedulera PBS: pbs_sched
Group:		Applications/Networking
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}

%description sched
This package contains the PBS scheduler daemon pbs_sched executable
and startup script.

%description sched -l pl
Ten pakiet zawiera demona schedulera pbs_sched i jego skrypt startowy.

%prep
%setup -q -n %{name}_%(echo %{version} | tr . _)
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
#cp %{SOURCE5} .
#cp %{SOURCE6} .
cp %{SOURCE7} .
#cp %{SOURCE8} .
patch -p1 < %{SOURCE8}

%build
pbs_server_home=/var/spool/pbs

./configure --prefix=${_prefix} --set-server-home=${pbs_server_home} --mandir=$RPM_BUILD_ROOT%{_mandir} --enable-docs --enable-server --enable-mom --enable-clients --disable-gui --set-default-server=localhost --enable-tcl-qstat --with-scp --with-tcl --enable-syslog
%{__make}
cp buildutils/pbs_mkdirs buildutils/pbs_mkdirs.orig
cp src/scheduler.cc/samples/fifo/Makefile src/scheduler.cc/samples/fifo/Makefile.orig

%install

# make directories
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT%{_datadir}
install -d $RPM_BUILD_ROOT/var/spool/pbs
# kludge pbs_mkdirs to create things in $RPM_BUILD_ROOT

cat buildutils/pbs_mkdirs.orig | sed -e 's|%{_prefix}|$RPM_BUILD_ROOT%{_prefix}|' | sed -e 's|/var/spool|$RPM_BUILD_ROOT/var/spool|' >buildutils/pbs_mkdirs
# kludge scheduler install
cat src/scheduler.cc/samples/fifo/Makefile.orig | sed -e 's|%{_prefix}|$(RPM_BUILD_ROOT)%{_prefix}|' | sed -e 's|/var/spool|$(RPM_BUILD_ROOT)/var/spool|' >src/scheduler.cc/samples/fifo/Makefile
# run make install
#make install prefix=$RPM_BUILD_ROOT/usr PBS_SERVER_HOME=$RPM_BUILD_ROOT/var/spool/pbs
%{__make} install prefix=$RPM_BUILD_ROOT%{_prefix}
# copy docs
#cp INSTALL PBS_License.text Read.Me Release_Notes $RPM_BUILD_ROOT/usr
# copy startup files
cp pbs_mom pbs_server pbs_sched $RPM_BUILD_ROOT/etc/rc.d/init.d
# copy scripts
#cp pbsenv.sh pbsenv.csh $RPM_BUILD_ROOT/usr/bin
cp pbsrun pbsconfig $RPM_BUILD_ROOT%{_bindir}
# make sure all the config files exist
touch $RPM_BUILD_ROOT/var/spool/pbs/default_server
touch $RPM_BUILD_ROOT/var/spool/pbs/server_name
touch $RPM_BUILD_ROOT/var/spool/pbs/mom_priv/config
touch $RPM_BUILD_ROOT/var/spool/pbs/sched_priv/sched_config
touch $RPM_BUILD_ROOT/var/spool/pbs/server_priv/nodes

%clean
rm -rf $RPM_BUILD_ROOT

%post mom
/sbin/chkconfig --add pbs_mom
if [ -f /var/lock/subsys/pbs_mom ]; then
	/etc/rc.d/init.d/pbs_mom restart >/dev/null 2>&1
else
	echo "Run \"/etc/rc.d/init.d/pbs_mom start\" to start pbs_mom daemon."
fi

%preun mom
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/pbs_mom ]; then
		/etc/rc.d/init.d/pbs_mom stop >&2
	fi
	/sbin/chkconfig --del pbs_mom
fi

%post server
/sbin/chkconfig --add pbs_server
if [ -f /var/lock/subsys/pbs_server ]; then
	/etc/rc.d/init.d/pbs_server restart >/dev/null 2>&1
else
	echo "Run \"/etc/rc.d/init.d/pbs_server start\" to start pbs_server daemon."
fi

%preun server
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/pbs_server ]; then
		/etc/rc.d/init.d/pbs_server stop >&2
	fi
	/sbin/chkconfig --del pbs_server
fi

%post sched
/sbin/chkconfig --add pbs_sched
if [ -f /var/lock/subsys/pbs_shed ]; then
	/etc/rc.d/init.d/pbs_shed restart >/dev/null 2>&1
else
	echo "Run \"/etc/rc.d/init.d/pbs_shed start\" to start pbs_shed daemon."
fi

%preun sched
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/pbs_sched ]; then
		/etc/rc.d/init.d/pbs_sched stop >&2
	fi
	/sbin/chkconfig --del pbs_sched
fi

%files
%defattr(644,root,root,755)
%doc INSTALL PBS_License.text Read.Me Release_Notes
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/default_server
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/pbs_environment
%attr(755,root,root) %{_bindir}/chk_tree
%attr(755,root,root) %{_bindir}/hostn
%attr(755,root,root) %{_bindir}/nqs2pbs
%attr(755,root,root) %{_bindir}/pbs_tclsh
%attr(755,root,root) %{_bindir}/pbsconfig
%attr(755,root,root) %{_bindir}/pbsdsh
#/usr/bin/pbsenv.csh
#/usr/bin/pbsenv.sh
%attr(755,root,root) %{_bindir}/pbsnodes
%attr(755,root,root) %{_bindir}/pbsrun
%attr(755,root,root) %{_bindir}/printjob
%attr(755,root,root) %{_bindir}/qalter
%attr(755,root,root) %{_bindir}/qdel
%attr(755,root,root) %{_bindir}/qdisable
%attr(755,root,root) %{_bindir}/qenable
%attr(755,root,root) %{_bindir}/qhold
%attr(755,root,root) %{_bindir}/qmgr
%attr(755,root,root) %{_bindir}/qmove
%attr(755,root,root) %{_bindir}/qmsg
%attr(755,root,root) %{_bindir}/qorder
%attr(755,root,root) %{_bindir}/qrerun
%attr(755,root,root) %{_bindir}/qrls
%attr(755,root,root) %{_bindir}/qrun
%attr(755,root,root) %{_bindir}/qselect
%attr(755,root,root) %{_bindir}/qsig
%attr(755,root,root) %{_bindir}/qstart
%attr(755,root,root) %{_bindir}/qstat
%attr(755,root,root) %{_bindir}/qstop
%attr(755,root,root) %{_bindir}/qsub
%attr(755,root,root) %{_bindir}/qterm
%attr(755,root,root) %{_bindir}/tracejob
%attr(755,root,root) %{_sbindir}/pbs_demux
%attr(4755,root,root) %{_sbindir}/pbs_iff
%attr(755,root,root) %{_sbindir}/pbs_rcp
%{_libdir}/libattr.a
%{_libdir}/libcmds.a
%{_libdir}/liblog.a
%{_libdir}/libnet.a
%{_libdir}/libpbs.a
%{_libdir}/libsite.a
%{_libdir}/pbs_sched.a
#/usr/lib/pbs
%{_includedir}/pbs_error.h
%{_includedir}/pbs_ifl.h
%{_includedir}/tm.h
%{_includedir}/tm_.h
%doc %{_mandir}

%files mom
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/pbs_mom
%attr(755,root,root) %{_sbindir}/pbs_mom
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/mom_priv/config
%dir /var/spool/pbs/mom_priv
%dir /var/spool/pbs/mom_priv/jobs
%dir /var/spool/pbs/mom_logs

%files server
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/pbs_server
%attr(755,root,root) %{_sbindir}/pbs_server
%dir /var/spool/pbs/server_priv
%dir /var/spool/pbs/server_priv/jobs
%dir /var/spool/pbs/server_priv/queues
%dir /var/spool/pbs/server_priv/acl_svr
%dir /var/spool/pbs/server_priv/acl_hosts
%dir /var/spool/pbs/server_priv/acl_users
%dir /var/spool/pbs/server_priv/acl_groups
%dir /var/spool/pbs/server_priv/accounting
%dir /var/spool/pbs/server_logs
%dir /var/spool/pbs
%dir /var/spool/pbs/spool
%dir /var/spool/pbs/aux
%dir /var/spool/pbs/checkpoint
%dir /var/spool/pbs/undelivered
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/server_name
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/server_priv/nodes

%files sched
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/pbs_sched
%attr(755,root,root) %{_sbindir}/pbs_sched
%dir /var/spool/pbs/sched_priv
%dir /var/spool/pbs/sched_logs
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/sched_priv/sched_config
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/sched_priv/resource_group
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/sched_priv/holidays
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /var/spool/pbs/sched_priv/dedicated_time
