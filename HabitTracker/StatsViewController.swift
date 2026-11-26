import UIKit

/// "Statistics": summary tiles, level, 4-week activity grid, streaks and badges.
final class StatsViewController: UIViewController {
    @IBOutlet weak var weekLabel: UILabel!
    @IBOutlet weak var bestLabel: UILabel!
    @IBOutlet weak var activeLabel: UILabel!
    @IBOutlet weak var levelLabel: UILabel!
    @IBOutlet weak var xpLabel: UILabel!
    @IBOutlet weak var xpBar: ProgressBarView!
    @IBOutlet weak var toNextLabel: UILabel!
    @IBOutlet weak var heatmapView: HeatmapView!
    @IBOutlet weak var streaksStack: UIStackView!
    @IBOutlet weak var badgesStack: UIStackView!

    private let store = HabitStore.shared

    override var preferredStatusBarStyle: UIStatusBarStyle { return .lightContent }

    override func viewDidLoad() {
        super.viewDidLoad()
        NotificationCenter.default.addObserver(self, selector: #selector(reload),
                                               name: .habitStoreChanged, object: nil)
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        store.rollOver()
        reload()
    }

    @IBAction func backTapped(_ sender: Any) {
        navigationController?.popViewController(animated: true)
    }

    @objc private func reload() {
        guard isViewLoaded else { return }
        let now = Date()

        weekLabel.text = "\(Int((store.weekRate(now: now) * 100).rounded()))%"
        bestLabel.text = "\(store.bestStreak)"
        activeLabel.text = "\(store.habits.count)"

        levelLabel.text = "Level \(store.level)"
        xpLabel.text = "\(store.xp) XP"
        xpBar.progress = CGFloat(store.levelProgress)
        toNextLabel.text = "\(store.xpToNextLevel) XP to Level \(store.level + 1)"

        heatmapView.configure(weeks: heatWeeks(now: now))
        rebuildStreaks()
        rebuildBadges()
    }

    /// Four Monday-first weeks; the last row is the current week.
    private func heatWeeks(now: Date) -> [[HeatCell]] {
        var calendar = Calendar(identifier: .gregorian)
        calendar.firstWeekday = 2
        let today = calendar.startOfDay(for: now)
        let weekdayIndex = store.weekdayIndex(today)
        guard let monday = calendar.date(byAdding: .day, value: -weekdayIndex, to: today) else { return [] }

        var weeks: [[HeatCell]] = []
        for week in 0..<4 {
            var row: [HeatCell] = []
            for day in 0..<7 {
                let offset = (week - 3) * 7 + day
                guard let date = calendar.date(byAdding: .day, value: offset, to: monday) else { continue }
                if date > today {
                    row.append(HeatCell(level: 0, isFuture: true, isToday: false))
                } else {
                    let level = HeatmapView.level(for: store.ratio(on: date, now: now))
                    row.append(HeatCell(level: level, isFuture: false, isToday: date == today))
                }
            }
            weeks.append(row)
        }
        return weeks
    }

    private func rebuildStreaks() {
        for view in streaksStack.arrangedSubviews {
            streaksStack.removeArrangedSubview(view)
            view.removeFromSuperview()
        }
        let active = store.habits.filter { $0.streak > 0 }
        if active.isEmpty {
            streaksStack.addArrangedSubview(StreakRowView(emptyMessage: "No active streaks yet"))
            return
        }
        for habit in active {
            streaksStack.addArrangedSubview(StreakRowView(habit: habit))
        }
    }

    private func rebuildBadges() {
        for view in badgesStack.arrangedSubviews {
            badgesStack.removeArrangedSubview(view)
            view.removeFromSuperview()
        }
        let definitions = HabitStore.badgeDefinitions
        for rowIndex in 0..<2 {
            let row = UIStackView()
            row.axis = .horizontal
            row.distribution = .fillEqually
            row.alignment = .top
            row.spacing = 8
            for column in 0..<3 {
                let index = rowIndex * 3 + column
                guard index < definitions.count else { continue }
                let info = definitions[index]
                row.addArrangedSubview(BadgeView(title: info.title, earned: store.isBadgeEarned(info.id)))
            }
            badgesStack.addArrangedSubview(row)
        }
    }
}
