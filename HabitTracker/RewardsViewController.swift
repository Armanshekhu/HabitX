import UIKit

/// "How rewards work": static explanation cards (laid out in the storyboard).
final class RewardsViewController: UIViewController {
    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    @IBAction func backTapped(_ sender: Any) {
        navigationController?.popViewController(animated: true)
    }
}
