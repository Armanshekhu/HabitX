import UIKit

/// Navigation stack with the system bar hidden (the design draws its own nav row)
/// while keeping the interactive swipe-back gesture.
final class HTNavigationController: UINavigationController, UIGestureRecognizerDelegate {
    override func viewDidLoad() {
        super.viewDidLoad()
        setNavigationBarHidden(true, animated: false)
        view.backgroundColor = Theme.background
        interactivePopGestureRecognizer?.delegate = self
    }

    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    func gestureRecognizerShouldBegin(_ gestureRecognizer: UIGestureRecognizer) -> Bool {
        return viewControllers.count > 1
    }
}
