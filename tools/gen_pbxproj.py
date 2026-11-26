#!/usr/bin/env python3
import hashlib, os
def uid(s): return hashlib.md5(s.encode()).hexdigest()[:24].upper()

swift = ['AppDelegate.swift', 'SceneDelegate.swift', 'Theme.swift', 'Icons.swift', 'IconData.swift', 'HabitStore.swift', 'Components.swift',
         'ListViews.swift', 'HTNavigationController.swift', 'SplashViewController.swift', 'TodayViewController.swift',
         'StatsViewController.swift', 'NewHabitViewController.swift', 'RewardsViewController.swift']
resources = [('Assets.xcassets', 'folder.assetcatalog'), ('Main.storyboard', 'file.storyboard'), ('LaunchScreen.storyboard', 'file.storyboard')]
for n in swift + [r[0] for r in resources] + ['Info.plist']:
    assert os.path.exists('../HabitTracker/' + n), n

P, TGT, APP, GRP, PGRP, MAIN = uid('proj'), uid('target'), uid('app'), uid('group'), uid('products'), uid('main')
fr = lambda n: uid('fr' + n); bf = lambda n: uid('bf' + n)
L = []
L.append('// !$*UTF8*$!\n{\n\tarchiveVersion = 1;\n\tclasses = {\n\t};\n\tobjectVersion = 56;\n\tobjects = {\n')
L.append('/* Begin PBXBuildFile section */')
for n in swift: L.append(f'\t\t{bf(n)} /* {n} in Sources */ = {{isa = PBXBuildFile; fileRef = {fr(n)} /* {n} */; }};')
for n, _ in resources: L.append(f'\t\t{bf(n)} /* {n} in Resources */ = {{isa = PBXBuildFile; fileRef = {fr(n)} /* {n} */; }};')
L.append('/* End PBXBuildFile section */\n\n/* Begin PBXFileReference section */')
for n in swift: L.append(f'\t\t{fr(n)} /* {n} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {n}; sourceTree = "<group>"; }};')
for n, t in resources: L.append(f'\t\t{fr(n)} /* {n} */ = {{isa = PBXFileReference; lastKnownFileType = {t}; path = {n}; sourceTree = "<group>"; }};')
L.append(f'\t\t{fr("Info.plist")} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};')
L.append(f'\t\t{APP} /* HabitTracker.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = HabitTracker.app; sourceTree = BUILT_PRODUCTS_DIR; }};')
L.append('/* End PBXFileReference section */\n')
FP, SP, RP = uid('frameworks'), uid('sources'), uid('resources')
L.append(f'/* Begin PBXFrameworksBuildPhase section */\n\t\t{FP} /* Frameworks */ = {{\n\t\t\tisa = PBXFrameworksBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};\n/* End PBXFrameworksBuildPhase section */\n')
kids = ',\n'.join(f'\t\t\t\t{fr(n)} /* {n} */' for n in swift + [r[0] for r in resources] + ['Info.plist'])
L.append(f'/* Begin PBXGroup section */\n\t\t{MAIN} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{GRP} /* HabitTracker */,\n\t\t\t\t{PGRP} /* Products */,\n\t\t\t);\n\t\t\tsourceTree = "<group>";\n\t\t}};')
L.append(f'\t\t{GRP} /* HabitTracker */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n{kids},\n\t\t\t);\n\t\t\tpath = HabitTracker;\n\t\t\tsourceTree = "<group>";\n\t\t}};')
L.append(f'\t\t{PGRP} /* Products */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{APP} /* HabitTracker.app */,\n\t\t\t);\n\t\t\tname = Products;\n\t\t\tsourceTree = "<group>";\n\t\t}};\n/* End PBXGroup section */\n')
TC, PC = uid('tcfg'), uid('pcfg')
L.append(f'/* Begin PBXNativeTarget section */\n\t\t{TGT} /* HabitTracker */ = {{\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = {TC} /* Build configuration list for PBXNativeTarget "HabitTracker" */;\n\t\t\tbuildPhases = (\n\t\t\t\t{SP} /* Sources */,\n\t\t\t\t{FP} /* Frameworks */,\n\t\t\t\t{RP} /* Resources */,\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t);\n\t\t\tname = HabitTracker;\n\t\t\tproductName = HabitTracker;\n\t\t\tproductReference = {APP} /* HabitTracker.app */;\n\t\t\tproductType = "com.apple.product-type.application";\n\t\t}};\n/* End PBXNativeTarget section */\n')
L.append(f'/* Begin PBXProject section */\n\t\t{P} /* Project object */ = {{\n\t\t\tisa = PBXProject;\n\t\t\tattributes = {{\n\t\t\t\tBuildIndependentTargetsInParallel = 1;\n\t\t\t\tLastSwiftUpdateCheck = 1500;\n\t\t\t\tLastUpgradeCheck = 1500;\n\t\t\t\tTargetAttributes = {{\n\t\t\t\t\t{TGT} = {{\n\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;\n\t\t\t\t\t}};\n\t\t\t\t}};\n\t\t\t}};\n\t\t\tbuildConfigurationList = {PC} /* Build configuration list for PBXProject "HabitTracker" */;\n\t\t\tcompatibilityVersion = "Xcode 14.0";\n\t\t\tdevelopmentRegion = en;\n\t\t\thasScannedForEncodings = 0;\n\t\t\tknownRegions = (\n\t\t\t\ten,\n\t\t\t\tBase,\n\t\t\t);\n\t\t\tmainGroup = {MAIN};\n\t\t\tproductRefGroup = {PGRP} /* Products */;\n\t\t\tprojectDirPath = "";\n\t\t\tprojectRoot = "";\n\t\t\ttargets = (\n\t\t\t\t{TGT} /* HabitTracker */,\n\t\t\t);\n\t\t}};\n/* End PBXProject section */\n')
rf = ',\n'.join(f'\t\t\t\t{bf(n)} /* {n} in Resources */' for n, _ in resources)
L.append(f'/* Begin PBXResourcesBuildPhase section */\n\t\t{RP} /* Resources */ = {{\n\t\t\tisa = PBXResourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{rf},\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};\n/* End PBXResourcesBuildPhase section */\n')
sf = ',\n'.join(f'\t\t\t\t{bf(n)} /* {n} in Sources */' for n in swift)
L.append(f'/* Begin PBXSourcesBuildPhase section */\n\t\t{SP} /* Sources */ = {{\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{sf},\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};\n/* End PBXSourcesBuildPhase section */\n')

def cfg(name, settings):
    body = ''.join(f'\t\t\t\t{k} = {v};\n' for k, v in settings.items())
    return f'\t\t{uid(name)} /* {name.split(":")[1]} */ = {{\n\t\t\tisa = XCBuildConfiguration;\n\t\t\tbuildSettings = {{\n{body}\t\t\t}};\n\t\t\tname = {name.split(":")[1]};\n\t\t}};'
common = {'ALWAYS_SEARCH_USER_PATHS': 'NO', 'CLANG_ANALYZER_NONNULL': 'YES', 'CLANG_ENABLE_MODULES': 'YES', 'CLANG_ENABLE_OBJC_ARC': 'YES',
          'COPY_PHASE_STRIP': 'NO', 'GCC_NO_COMMON_BLOCKS': 'YES', 'IPHONEOS_DEPLOYMENT_TARGET': '15.0', 'SDKROOT': 'iphoneos',
          'ENABLE_USER_SCRIPT_SANDBOXING': 'YES'}
dbg = dict(common, **{'DEBUG_INFORMATION_FORMAT': 'dwarf', 'ENABLE_TESTABILITY': 'YES', 'GCC_DYNAMIC_NO_PIC': 'NO', 'GCC_OPTIMIZATION_LEVEL': '0',
                      'GCC_PREPROCESSOR_DEFINITIONS': '(\n\t\t\t\t\t"DEBUG=1",\n\t\t\t\t\t"$(inherited)",\n\t\t\t\t)', 'MTL_ENABLE_DEBUG_INFO': 'INCLUDE_SOURCE',
                      'ONLY_ACTIVE_ARCH': 'YES', 'SWIFT_ACTIVE_COMPILATION_CONDITIONS': '"$(inherited) DEBUG"', 'SWIFT_OPTIMIZATION_LEVEL': '"-Onone"'})
rel = dict(common, **{'DEBUG_INFORMATION_FORMAT': '"dwarf-with-dsym"', 'ENABLE_NS_ASSERTIONS': 'NO', 'MTL_ENABLE_DEBUG_INFO': 'NO',
                      'SWIFT_COMPILATION_MODE': 'wholemodule', 'VALIDATE_PRODUCT': 'YES'})
tgt = {'ASSETCATALOG_COMPILER_APPICON_NAME': 'AppIcon', 'CODE_SIGN_STYLE': 'Automatic', 'CURRENT_PROJECT_VERSION': '1',
       'GENERATE_INFOPLIST_FILE': 'NO', 'INFOPLIST_FILE': 'HabitTracker/Info.plist',
       'LD_RUNPATH_SEARCH_PATHS': '(\n\t\t\t\t\t"$(inherited)",\n\t\t\t\t\t"@executable_path/Frameworks",\n\t\t\t\t)',
       'MARKETING_VERSION': '1.0', 'PRODUCT_BUNDLE_IDENTIFIER': 'com.example.HabitTracker', 'PRODUCT_NAME': '"$(TARGET_NAME)"',
       'SWIFT_VERSION': '5.0', 'TARGETED_DEVICE_FAMILY': '1'}
L.append('/* Begin XCBuildConfiguration section */')
L += [cfg('P:Debug', dbg), cfg('P:Release', rel), cfg('T:Debug', tgt), cfg('T:Release', tgt)]
L.append('/* End XCBuildConfiguration section */\n')
L.append('/* Begin XCConfigurationList section */')
L.append(f'\t\t{PC} /* Build configuration list for PBXProject "HabitTracker" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{uid("P:Debug")} /* Debug */,\n\t\t\t\t{uid("P:Release")} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};')
L.append(f'\t\t{TC} /* Build configuration list for PBXNativeTarget "HabitTracker" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{uid("T:Debug")} /* Debug */,\n\t\t\t\t{uid("T:Release")} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};')
L.append('/* End XCConfigurationList section */\n\t};\n\trootObject = ' + P + ' /* Project object */;\n}\n')
open('../HabitTracker.xcodeproj/project.pbxproj', 'w').write('\n'.join(L))
print('pbxproj written')
