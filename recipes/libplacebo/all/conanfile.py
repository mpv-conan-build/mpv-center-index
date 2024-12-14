from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.cmake import CMakeToolchain
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Git

import os
from pathlib import Path

required_conan_version = ">=2.0.0"

class LibplaceboConan(ConanFile):
    name = "libplacebo"
    description = "Reusable library for GPU-accelerated video/image rendering"
    homepage = "https://code.videolan.org/videolan/libplacebo"
    license = "LGPL-2.1-or-later"
    topics = ("gpu", "rendering", "video", "image")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "vulkan": [True, False],
        "vk_proc_addr": [True, False],
        "opengl": [True, False],
        "gl_proc_addr": [True, False],
        "d3d11": [True, False],
        "glslang": [True, False],
        "shaderc": [True, False],
        "lcms": [True, False],
        "dovi": [True, False],
        "libdovi": [True, False],
        "unwind": [True, False],
        "xxhash": [True, False],
        "debug_abort": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debug_abort": False,
    }
    
    def source(self):
        git = Git(self)
        git.clone(url=self.conan_data["sources"][self.version]["url"], target=self.source_folder, args=["--recursive", "--depth=1", "--branch", f"v{self.version}"])
    
    def layout(self):
        basic_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Windows":
            del self.options.d3d11

    def configure(self):
        if self.options.get_safe("vulkan") == None:
            self.options.vulkan = True
        if self.settings.get_safe("vk_proc_addr") == None:
            self.options.vk_proc_addr = False

        if self.options.get_safe("opengl") == None:
            self.options.opengl = True
        if self.settings.get_safe("gl_proc_addr") == None:
            self.options.gl_proc_addr = False

        if self.options.get_safe("glslang") == None and self.options.get_safe("shaderc") == None:
            self.options.shaderc = True
            self.options.glslang = False

        if self.options.get_safe("lcms") == None:
            self.options.lcms = True
        
        if self.options.get_safe("dovi") == None:
            self.options.dovi = True
        if self.options.get_safe("dovi") == True:
            self.options.libdovi = True

        if self.options.get_safe("unwind") == None:
            self.options.unwind = False

        if self.options.get_safe("xxhash") == None:
            self.options.xxhash = True
        
        if self.settings.os == "Windows":
            if self.options.get_safe("d3d11") == None:
                self.options.d3d11 = True
    
    def validate(self):
        if check_min_cppstd(self, 20):
            raise ConanInvalidConfiguration("C++20 is required")
        if self.options.get_safe("vulkan") == False and self.settings.get_safe("vk_proc_addr") == True:
            raise ConanInvalidConfiguration("vk_proc_addr cannot be enabled if vulkan is disabled")
        if self.options.get_safe("opengl") == False and self.settings.get_safe("gl_proc_addr") == True:
            raise ConanInvalidConfiguration("gl_proc_addr cannot be enabled if opengl is disabled")
        if self.options.get_safe("libdovi") == True and self.options.get_safe("dovi") == False:
            raise ConanInvalidConfiguration("libdovi cannot be enabled if dovi is disabled")

    def requirements(self):
        if self.options.lcms == True:
            self.requires("lcms/[>=2.9]")
        if self.options.libdovi == True:
            self.requires("libdovi/[>=1.6.7]")
        if self.options.xxhash == True:
            self.requires("xxhash/[>0.8.0]")
        if self.options.shaderc == True:
            self.requires("shaderc/[>=2019.1]")
        if self.options.glslang == True:
            self.requires("glslang/[>=1.3.0]")
            self.requires("spirv-tools/[>1.2]") 

        if self.options.vulkan == True:
            if self.options.vk_proc_addr == True:
                self.requires("vulkan-headers/[>=1.3.268.0]")
            else:
                self.requires("vulkan-loader/[>=1.3.268.0]")
        
        if self.options.opengl == True:
            if not self.options.get_safe("gl_proc_addr"):
                self.requires("opengl/system")
                if self.settings.os != "Windows":
                    self.requires("egl/system")

        if self.options.unwind == True and self.settings.os != "Windows":
            self.requires("libunwind/[>=1.6.2]")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.5]")
        self.tool_requires("pkgconf/[>=2.0.0]")
        if self.options.get_safe("glslang"):
            self.tool_requires("cmake/[>=3.24]")  # For finding SPIRV components

    def generate(self):
        if self.options.get_safe("glslang"):
            tc = CMakeToolchain(self)
            tc.generate()

        pc = PkgConfigDeps(self)
        pc.generate()

        tc = MesonToolchain(self)
    
        tc.project_options.update({
            "demos": "false",
            "tests": "false",
            "bench": "false",
            "fuzz": "false",
        })

        feature_options = {
            "vulkan": "vulkan",
            "vk-proc-addr":"vk_proc_addr",
            "opengl": "opengl",
            "gl-proc-addr": "gl_proc_addr",
            "d3d11": "d3d11",
            "glslang": "glslang",
            "shaderc": "shaderc",
            "lcms": "lcms",
            "dovi": "dovi",
            "libdovi": "libdovi",
            "unwind": "unwind",
            "xxhash": "xxhash",
        }
        tc.project_options.update({ 
            option : ("enabled" if self.options.get_safe(value) else "disabled")
                for option, value in feature_options.items() 
        })

        boolean_options = {
            "debug-abort": "debug_abort",
        }
        tc.project_options.update({
            option : ("true" if self.options.get_safe(value) else "false")
                for option, value in boolean_options.items()
        })
        
        tc.generate()
        

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["placebo"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["shlwapi"])
        # Set defines based on options
        self.cpp_info.defines.append("PL_EXPORT")
        if not self.options.get_safe("shared"):
            self.cpp_info.defines.append("PL_STATIC")
        
        pkgconfig_options = [
            "d3d11",
            "dovi",
            "gl_proc_addr",
            "glslang",
            "lcms",
            "libdovi",
            "opengl",
            "shaderc",
            "vk_proc_addr",
            "vulkan",
            "xxhash"
        ]

        self.cpp_info.set_property("pkg_config_custom_content",
                    { f"pl_has_{option}": "1" if self.options[option] else "0" for option in pkgconfig_options })


