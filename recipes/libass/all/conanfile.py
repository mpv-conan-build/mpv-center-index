from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.apple import is_apple_os
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.0"

class LibassConan(ConanFile):
    name = "libass"
    description = "LibASS is an SSA/ASS subtitles rendering library"
    license = "ISC"
    topics = ("subtitles", "video", "rendering", "SSA", "ASS")
    homepage = "https://github.com/libass/libass"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fontconfig": [True, False],
        "directwrite": [True, False],
        "coretext": [True, False],
        "asm": [True, False],
        "libunibreak": [True, False],
        "require_system_font_provider": [True, False],
        "large_tiles": [True, False],
    }
    
    default_options = {
        "shared": False,
        "fPIC": True,
        "libunibreak": False,
        "require_system_font_provider": True,
        "large_tiles": False,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.options.require_system_font_provider:
            if self.settings.os == "Windows":
                del self.options.fPIC
            
            if self.settings.os != "Windows":
                self.options.rm_safe("directwrite")
            if not is_apple_os(self):
                self.options.rm_safe("coretext")

        # ASM is only supported on x86 and aarch64
        if self.settings.arch not in ["x86", "x86_64", "armv8"]:
            self.options.rm_safe("asm")

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        match self.settings.os:
            case "Windows":
                if self.options.get_safe("directwrite") == None:
                    self.options.directwrite = True
            case "Macos":
                if self.options.get_safe("coretext") == None:
                    self.options.coretext = True
            case _:
                if self.options.get_safe("fontconfig") == None:
                    self.options.fontconfig = True

        if self.settings.arch in ["x86", "x86_64", "armv8"]:
            if self.options.asm == None:
                self.options.asm = True


    def requirements(self):
        self.requires("libpng/[>=1.6]")
        self.requires("freetype/[>=2.13]")
        self.requires("fribidi/[>=1.0]")
        self.requires("harfbuzz/[>=7.3]")
        
        if self.options.libunibreak:
            self.requires("libunibreak/[>=5.1]")
        
        if self.options.fontconfig:
            self.requires("fontconfig/[>=2.14]")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.5]")
        self.tool_requires("pkgconf/[>=1.7]")
        if self.options.get_safe("asm"):
            self.tool_requires("nasm/[>=2.15]")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        pc = PkgConfigDeps(self)
        pc.generate()
        tc = MesonToolchain(self)

        features_options = {
            "fontconfig": "fontconfig",
            "directwrite": "directwrite",
            "coretext": "coretext",
            "asm": "asm",
            "libunibreak": "libunibreak",
        }
        tc.project_options.update({ 
            option : ("enabled" if bool(self.options.get_safe(value)) else "disabled")
                for option, value in features_options.items() 
        })

        boolean_options = {
            "require-system-font-provider": "require_system_font_provider",
            "large-tiles": "large_tiles"
        }
        tc.project_options.update({ 
            option : ("true" if bool(self.options.get_safe(value)) else "false") 
                for option, value in boolean_options.items() 
        })

        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "ISC", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["ass"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        elif self.settings.os == "Windows":
            if self.options.directwrite:
                self.cpp_info.system_libs = ["dwrite"] if self.settings.os.subsystem == "uwp" else ["gdi32"]