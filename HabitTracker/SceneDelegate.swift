import UIKit

/// With `UISceneStoryboardFile` set in Info.plist, UIKit loads Main.storyboard
/// and assigns the window automatically.
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard scene is UIWindowScene else { return }
        window?.overrideUserInterfaceStyle = .dark
    }
}
