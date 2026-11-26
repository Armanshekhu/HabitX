import UIKit

/// Splash: logo, title, tagline and a loading bar that fills before handing off to the app.
final class SplashViewController: UIViewController {
    @IBOutlet weak var progressBar: ProgressBarView!
    private var didStart = false

    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard !didStart else { return }
        didStart = true

        // Design shows the bar at 60% — hold that frame briefly, then finish loading.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.progressBar.setProgress(1, animated: true, duration: 0.7)
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) { [weak self] in
            self?.performSegue(withIdentifier: "showMain", sender: nil)
        }
    }

    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        segue.destination.modalPresentationStyle = .fullScreen
        segue.destination.modalTransitionStyle = .crossDissolve
    }
}
