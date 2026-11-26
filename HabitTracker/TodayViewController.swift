import UIKit

/// "Today": XP / level card, daily progress and the list of habits scheduled today.
final class TodayViewController: UIViewController {
    @IBOutlet weak var dateLabel: UILabel!
    @IBOutlet weak var levelLabel: UILabel!
    @IBOutlet weak var xpLabel: UILabel!
    @IBOutlet weak var streakLabel: UILabel!
    @IBOutlet weak var xpBar: ProgressBarView!
    @IBOutlet weak var toNextLabel: UILabel!
    @IBOutlet weak var progressCountLabel: UILabel!
    @IBOutlet weak var progressBar: ProgressBarView!
    @IBOutlet weak var perfectLabel: UILabel!
    @IBOutlet weak var habitsStack: UIStackView!

    private let store = HabitStore.shared

    private lazy var dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.setLocalizedDateFormatFromTemplate("EEEEMMMMd")   // "Tuesday, November 24"
        return formatter
    }()

    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    override func viewDidLoad() {
        super.viewDidLoad()
        let center = NotificationCenter.default
        center.addObserver(self, selector: #selector(reload), name: .habitStoreChanged, object: nil)
        center.addObserver(self, selector: #selector(dayMayHaveChanged),
                           name: UIApplication.willEnterForegroundNotification, object: nil)
        center.addObserver(self, selector: #selector(dayMayHaveChanged),
                           name: UIApplication.significantTimeChangeNotification, object: nil)
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        store.rollOver()
        reload()
    }

    @objc private func dayMayHaveChanged() {
        store.rollOver()
        reload()
    }

    @objc private func reload() {
        guard isViewLoaded else { return }
        let now = Date()
        let animate = view.window != nil

        dateLabel.text = dateFormatter.string(from: now)
        levelLabel.text = "Level \(store.level)"
        xpLabel.attributedText = xpText(store.xp)
        streakLabel.text = store.dayStreak > 0 ? "\(store.dayStreak) day streak" : "Start a streak"
        xpBar.setProgress(CGFloat(store.levelProgress), animated: animate)
        toNextLabel.text = "\(store.xpToNextLevel) XP to Level \(store.level + 1)"

        let scheduled = store.scheduledToday(now: now)
        let done = scheduled.filter { store.isDone($0, now: now) }.count
        progressCountLabel.text = "\(done) / \(scheduled.count)"
        progressBar.setProgress(scheduled.isEmpty ? 0 : CGFloat(done) / CGFloat(scheduled.count), animated: animate)

        if scheduled.isEmpty {
            perfectLabel.text = "Add a habit to start earning XP"
        } else if done == scheduled.count {
            perfectLabel.text = "Perfect day! +\(HabitStore.perfectDayBonus) XP earned"
        } else {
            perfectLabel.text = "Finish all \(scheduled.count) for a +\(HabitStore.perfectDayBonus) XP perfect day bonus"
        }

        rebuildHabits(scheduled, now: now)
    }

    /// "240 XP": 28pt heavy gold number + 15pt semibold grey unit (28pt × 1.1 line height).
    private func xpText(_ value: Int) -> NSAttributedString {
        let style = NSMutableParagraphStyle()
        style.minimumLineHeight = 30.8
        style.maximumLineHeight = 30.8
        let text = NSMutableAttributedString(string: "\(value)", attributes: [
            .font: Theme.font(28, .heavy),
            .foregroundColor: Theme.gold,
            .paragraphStyle: style
        ])
        text.append(NSAttributedString(string: " XP", attributes: [
            .font: Theme.font(15, .semibold),
            .foregroundColor: Theme.textSecondary,
            .paragraphStyle: style
        ]))
        return text
    }

    private func rebuildHabits(_ habits: [Habit], now: Date) {
        for view in habitsStack.arrangedSubviews {
            habitsStack.removeArrangedSubview(view)
            view.removeFromSuperview()
        }
        if habits.isEmpty {
            let empty = makeLabel("No habits scheduled today", size: 15, color: Theme.textTertiary)
            empty.textAlignment = .center
            habitsStack.addArrangedSubview(empty)
            return
        }
        for habit in habits {
            let card = HabitCardView(habit: habit, done: store.isDone(habit, now: now))
            let id = habit.id
            card.onToggle = { [weak self] in
                UIImpactFeedbackGenerator(style: .light).impactOccurred()
                self?.store.toggle(habitId: id)
            }
            habitsStack.addArrangedSubview(card)
        }
    }
}
