import UIKit

/// "New Habit": icon picker, name, weekday repeat and save / discard.
final class NewHabitViewController: UIViewController, UITextFieldDelegate {
    @IBOutlet weak var scrollView: UIScrollView!
    @IBOutlet weak var previewTile: IconTileView!
    @IBOutlet weak var iconGrid: UIStackView!
    @IBOutlet weak var nameField: PaddedTextField!
    @IBOutlet var dayButtons: [UIButton]!

    private static let iconNames = [
        "run", "read", "water", "meditate", "sleep",
        "code", "music", "cook", "journal", "gym",
        "yoga", "walk", "cycle", "study", "nophone",
        "vitamins", "language", "gratitude", "health", "organize"
    ]
    private static let dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    private var selectedIcon = "run"
    /// Monday … Sunday — design default is Monday–Friday.
    private var selectedDays: [Bool] = [true, true, true, true, true, false, false]
    private var iconButtons: [HTButton] = []

    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    override func viewDidLoad() {
        super.viewDidLoad()
        scrollView.keyboardDismissMode = .interactive
        nameField.delegate = self
        nameField.accessibilityLabel = "Name"

        buildIconGrid()
        let sortedDays = dayButtons.sorted { $0.tag < $1.tag }
        for (index, button) in sortedDays.enumerated() {
            button.accessibilityLabel = NewHabitViewController.dayNames[index]
            button.titleLabel?.font = Theme.font(15, .semibold)
        }
        refreshIconSelection()
        refreshDays()

        let tap = UITapGestureRecognizer(target: self, action: #selector(previewTapped))
        previewTile.isUserInteractionEnabled = true
        previewTile.addGestureRecognizer(tap)

        NotificationCenter.default.addObserver(self, selector: #selector(keyboardChanged(_:)),
                                               name: UIResponder.keyboardWillChangeFrameNotification, object: nil)
    }

    // MARK: Icon grid (5 × 4, 10pt gaps, square tiles)

    private func buildIconGrid() {
        let columns = 5
        let names = NewHabitViewController.iconNames
        var index = 0
        while index < names.count {
            let row = UIStackView()
            row.axis = .horizontal
            row.distribution = .fillEqually
            row.spacing = 10
            for _ in 0..<columns where index < names.count {
                let button = HTButton(type: .custom)
                button.translatesAutoresizingMaskIntoConstraints = false
                button.layer.cornerRadius = 10
                button.tag = index
                button.accessibilityLabel = "\(names[index]) icon"
                button.setImage(Icons.image(names[index], size: 28), for: .normal)
                button.addTarget(self, action: #selector(iconTapped(_:)), for: .touchUpInside)
                button.heightAnchor.constraint(equalTo: button.widthAnchor).isActive = true
                row.addArrangedSubview(button)
                iconButtons.append(button)
                index += 1
            }
            iconGrid.addArrangedSubview(row)
        }
    }

    private func refreshIconSelection() {
        let names = NewHabitViewController.iconNames
        for button in iconButtons {
            let selected = names[button.tag] == selectedIcon
            button.backgroundColor = selected ? Theme.accent : Theme.tile
            button.tintColor = selected ? .white : Theme.icon
        }
        previewTile.configure(icon: selectedIcon, iconSize: 32, radius: 16,
                              background: Theme.tile, tint: Theme.icon,
                              dash: Theme.accent, dashWidth: 1.5)
    }

    private func refreshDays() {
        for button in dayButtons {
            let on = selectedDays[button.tag]
            button.layer.cornerRadius = 12
            button.backgroundColor = on ? Theme.daySelected : Theme.card
            button.layer.borderWidth = on ? 1.5 : 1
            button.layer.borderColor = (on ? Theme.accent : Theme.fieldBorder).cgColor
            button.setTitleColor(on ? Theme.icon : Theme.textTertiary, for: .normal)
        }
    }

    // MARK: Actions

    @objc private func iconTapped(_ sender: UIButton) {
        selectedIcon = NewHabitViewController.iconNames[sender.tag]
        refreshIconSelection()
    }

    @objc private func previewTapped() {
        view.endEditing(true)
        let rect = iconGrid.convert(iconGrid.bounds, to: scrollView)
        scrollView.scrollRectToVisible(rect.insetBy(dx: 0, dy: -24), animated: true)
    }

    @IBAction func dayTapped(_ sender: UIButton) {
        selectedDays[sender.tag].toggle()
        refreshDays()
    }

    @IBAction func backTapped(_ sender: Any) {
        navigationController?.popViewController(animated: true)
    }

    @IBAction func discardTapped(_ sender: Any) {
        navigationController?.popViewController(animated: true)
    }

    @IBAction func saveTapped(_ sender: Any) {
        view.endEditing(true)
        let name = (nameField.text ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !name.isEmpty else {
            shake(nameField)
            return
        }
        guard selectedDays.contains(true) else {
            dayButtons.forEach { shake($0) }
            return
        }
        HabitStore.shared.addHabit(name: name, icon: selectedIcon, days: selectedDays)
        UINotificationFeedbackGenerator().notificationOccurred(.success)
        navigationController?.popViewController(animated: true)
    }

    private func shake(_ view: UIView) {
        let animation = CAKeyframeAnimation(keyPath: "transform.translation.x")
        animation.timingFunction = CAMediaTimingFunction(name: .linear)
        animation.duration = 0.4
        animation.values = [-8, 8, -6, 6, -3, 3, 0]
        view.layer.add(animation, forKey: "shake")
        UINotificationFeedbackGenerator().notificationOccurred(.error)
    }

    // MARK: Text field

    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        textField.resignFirstResponder()
        return true
    }

    func textField(_ textField: UITextField, shouldChangeCharactersIn range: NSRange,
                   replacementString string: String) -> Bool {
        let current = textField.text ?? ""
        guard let swiftRange = Range(range, in: current) else { return true }
        return current.replacingCharacters(in: swiftRange, with: string).count <= 50
    }

    // MARK: Keyboard

    @objc private func keyboardChanged(_ notification: Notification) {
        guard let value = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? NSValue else { return }
        let frame = view.convert(value.cgRectValue, from: nil)
        let overlap = max(0, view.bounds.maxY - frame.minY)
        scrollView.contentInset.bottom = overlap
        scrollView.verticalScrollIndicatorInsets.bottom = overlap
    }
}
