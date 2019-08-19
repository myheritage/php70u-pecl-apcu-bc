%global pecl_name apcu-bc
%global pecl_so_name apc
%global php_base %{?_php_base}%{?!_php_base:php72u}
%global ini_name  50-%{pecl_name}.ini
%global with_zts 0%{?__ztsphp:1}

%global gh_commit   f9856981eee0c8b3d1697f5b7bc6a9cffc413379
%global gh_short    %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner    krakjoe
%global gh_project  apcu-bc
%global gh_date     20160315

Summary: Extension to work with the Memcached caching daemon
Name: %{php_base}-pecl-%{pecl_name}
Version: 1.0.3
%if 0%{?gh_date:1}
Release: git%{gh_short}.1.MyHeritage.ius%{?dist}
%else
Release: 1.ius%{?dist}
%endif
License: PHP
Group: Development/Libraries
#Source0: http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz
%if 0%{?gh_date:1}
Source0:      https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{gh_commit}.tar.gz
%else
Source0:      http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
%endif
Source1: %{pecl_name}.ini
URL: http://pecl.php.net/package/%{pecl_name}
BuildRequires: pear1u
BuildRequires: %{php_base}-devel
BuildRequires: %{php_base}-pecl-apcu-devel
BuildRequires: zlib-devel
%if 0%{?fedora} < 24
Requires(post): pear1u
Requires(postun): pear1u
%endif
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}

# provide the stock name
Provides: php-pecl-%{pecl_name} = %{version}
Provides: php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides: php-%{pecl_name} = %{version}
Provides: php-%{pecl_name}%{?_isa} = %{version}
Provides: %{php_base}-%{pecl_name} = %{version}
Provides: %{php_base}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides: php-pecl(%{pecl_name}) = %{version}
Provides: php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides: %{php_base}-pecl(%{pecl_name}) = %{version}
Provides: %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts: php-pecl-%{pecl_name} < %{version}


# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
Memcached is a caching daemon designed especially for
dynamic web applications to decrease database load by
storing objects in memory.
This extension allows you to work with memcached through
handy OO and procedural interfaces.
Memcache can be used as a PHP session handler.


%prep
%setup -qc
%if 0%{?gh_date:1}
mv %{gh_project}-%{gh_commit} NTS
mv NTS/package.xml .
sed -e '/release/s/3.0.9/%{version}dev/' -i package.xml
%else
mv %{pecl_name}-%{version} NTS
%endif


%if %{with_zts}
cp -r NTS ZTS
%endif


%build
pushd NTS
phpize
%{configure} --with-%{pecl_name}=%{prefix} --with-php-config=%{_bindir}/php-config
%{__make}
popd

%if %{with_zts}
pushd ZTS
zts-phpize
%{configure} --with-%{pecl_name}=%{prefix} --with-php-config=%{_bindir}/zts-php-config
%{__make}
popd
%endif


%install
%{__make} install INSTALL_ROOT=%{buildroot} -C NTS

# Install XML package description
install -Dpm 0644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Install config file
install -Dpm 0644 %{SOURCE1} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
%{__make} install INSTALL_ROOT=%{buildroot} -C ZTS

# Install config file
install -Dpm 0644 %{SOURCE1} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

rm -rf %{buildroot}%{php_incldir}/ext/%{pecl_name}/
%if %{with_zts}
rm -rf %{buildroot}%{php_ztsincldir}/ext/%{pecl_name}/
%endif

# Documentation
for i in $(grep 'role="doc"' package.xml | grep 'file' | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done

%check
# Shared needed extensions
modules=""
for mod in apcu; do
  if [ -f %{php_extdir}/${mod}.so ]; then
    modules="$modules -d extension=${mod}.so"
  fi
done

# simple module load test
%{__php} \
    --no-php-ini \
    $modules \
    --define extension=%{buildroot}/%{php_extdir}/%{pecl_so_name}.so \
    --modules | grep %{pecl_so_name}
%if %{with_zts}
%{__ztsphp} \
    --no-php-ini \
    $modules \
    --define extension=%{buildroot}/%{php_ztsextdir}/%{pecl_so_name}.so \
    --modules | grep %{pecl_so_name}
%endif


%if 0%{?fedora} < 24
%post
%if 0%{?pecl_install:1}
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml
%endif


%postun
%if 0%{?pecl_uninstall:1}
if [ "$1" -eq "0" ]; then
%{pecl_uninstall} %{pecl_name}
fi
%endif
%endif


%files
%doc %{pecl_docdir}/%{pecl_name}
%{php_extdir}/%{pecl_so_name}.so
%{pecl_xmldir}/%{pecl_name}.xml
%config(noreplace) %verify(not md5 mtime size) %{php_inidir}/%{ini_name}

%if %{with_zts}
%{php_ztsextdir}/%{pecl_so_name}.so
%config(noreplace) %verify(not md5 mtime size) %{php_ztsinidir}/%{ini_name}
%endif


%changelog
