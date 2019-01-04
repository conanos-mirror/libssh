from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os, shutil


class LibsshConan(ConanFile):
    name = "libssh"
    version = "0.8.6"
    description = "Mulitplatform C library implementing the SSHv2 and SSHv1 protocol for client and server implementations"
    url = "https://github.com/conanos/libssh"
    homepage = "https://www.libssh.org/"
    license = "LGPL-v2.1+"
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("libgcrypt/1.8.4@conanos/stable")
        self.requires.add("zlib/1.2.11@conanos/stable")

    def source(self):
        url_ = 'https://github.com/ShiftMediaProject/libssh/archive/libssh-{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                for proj in ["libssh.vcxproj"]:
                    tools.replace_in_file(proj, "zlibd.lib","zlib.lib",strict=False)
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("libssh.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'},build_type=build_type)

    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            rplatform = platforms.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            if self.options.shared:
                for i in ["lib","bin"]:
                    self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

