using UnrealBuildTool;
using System.IO;

public class ZLAsr : ModuleRules
{
    public ZLAsr(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp17;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "Projects",
            "Json",
            "JsonUtilities"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Slate",
            "SlateCore"
        });

        PublicIncludePaths.Add(Path.Combine(ModuleDirectory, "Public"));
        PrivateIncludePaths.Add(Path.Combine(ModuleDirectory, "Private"));

        if (Target.Platform == UnrealTargetPlatform.Android)
        {
            PrivateDependencyModuleNames.Add("Launch");
            AdditionalPropertiesForReceipt.Add("AndroidPlugin", Path.Combine(ModuleDirectory, "ZLAsr_Android_UPL.xml"));
        }

        if (Target.Platform == UnrealTargetPlatform.IOS)
        {
            PublicFrameworks.AddRange(new string[]
            {
                "AVFoundation",
                "AudioToolbox"
            });

            PublicAdditionalFrameworks.Add(
                new Framework(
                    "QCloudRealTime",
                    "../ThirdParty/IOS/QCloudRealTime.xcframework.zip"
                )
            );
            PublicAdditionalFrameworks.Add(
                new Framework(
                    "QCloudOneSentence",
                    "../ThirdParty/IOS/QCloudOneSentence.xcframework.zip"
                )
            );
            PublicAdditionalFrameworks.Add(
                new Framework(
                    "QCloudFileRecognizer",
                    "../ThirdParty/IOS/QCloudFileRecognizer.xcframework.zip"
                )
            );
            PublicAdditionalFrameworks.Add(
                new Framework(
                    "VoiceCommon",
                    "../ThirdParty/IOS/VoiceCommon.framework.zip"
                )
            );
        }
    }
}
