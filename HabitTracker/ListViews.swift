import UIKit

// MARK: - Today: habit card

/// 68pt habit card: tile · title + streak · "+10 XP" · check circle.
final class HabitCardView: UIView {
    var onToggle: (() -> Void)?

    init(habit: Habit, done: Bool) {
        super.init(frame: .zero)
        translatesAutoresizingMaskIntoConstraints = false
        backgroundColor = Theme.card
        layer.cornerRadius = 14

        let tile = IconTileView()
        tile.translatesAutoresizingMaskIntoConstraints = false
        tile.configure(icon: habit.icon, iconSize: 22)

        let title = makeLabel(habit.name, size: 15, weight: .semibold)
        let subtitle = HabitCardView.makeSubtitle(habit)
        let textStack = UIStackView(arrangedSubviews: [title, subtitle])
        textStack.translatesAutoresizingMaskIntoConstraints = false
        textStack.axis = .vertical
        textStack.alignment = .leading
        textStack.spacing = 2

        let xpLabel = makeLabel("+\(HabitStore.xpPerCheckIn) XP", size: 12, weight: .semibold, color: Theme.gold)
        xpLabel.setContentHuggingPriority(.required, for: .horizontal)
        xpLabel.setContentCompressionResistancePriority(.required, for: .horizontal)

        let button = HTButton(type: .custom)
        button.translatesAutoresizingMaskIntoConstraints = false
        button.accessibilityLabel = "\(habit.name), \(done ? "Completed" : "Not completed")"
        button.addTarget(self, action: #selector(tapped), for: .touchUpInside)

        let circle = UIView()
        circle.translatesAutoresizingMaskIntoConstraints = false
        circle.isUserInteractionEnabled = false
        circle.layer.cornerRadius = 15
        if done {
            circle.backgroundColor = Theme.green
            let check = UIImageView(image: Icons.image("check", size: 18, stroke: 2.6))
            check.translatesAutoresizingMaskIntoConstraints = false
            check.tintColor = .white
            circle.addSubview(check)
            NSLayoutConstraint.activate([
                check.centerXAnchor.constraint(equalTo: circle.centerXAnchor),
                check.centerYAnchor.constraint(equalTo: circle.centerYAnchor)
            ])
        } else {
            circle.layer.borderWidth = 1.5
            circle.layer.borderColor = Theme.outline.cgColor
        }
        button.addSubview(circle)

        addSubview(tile)
        addSubview(textStack)
        addSubview(xpLabel)
        addSubview(button)

        NSLayoutConstraint.activate([
            heightAnchor.constraint(equalToConstant: 68),

            tile.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 12),
            tile.centerYAnchor.constraint(equalTo: centerYAnchor),
            tile.widthAnchor.constraint(equalToConstant: 42),
            tile.heightAnchor.constraint(equalToConstant: 42),

            textStack.leadingAnchor.constraint(equalTo: tile.trailingAnchor, constant: 12),
            textStack.centerYAnchor.constraint(equalTo: centerYAnchor),
            textStack.trailingAnchor.constraint(lessThanOrEqualTo: xpLabel.leadingAnchor, constant: -12),

            xpLabel.trailingAnchor.constraint(equalTo: button.leadingAnchor, constant: -12),
            xpLabel.centerYAnchor.constraint(equalTo: centerYAnchor),

            button.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -8),
            button.centerYAnchor.constraint(equalTo: centerYAnchor),
            button.widthAnchor.constraint(equalToConstant: 44),
            button.heightAnchor.constraint(equalToConstant: 44),

            circle.centerXAnchor.constraint(equalTo: button.centerXAnchor),
            circle.centerYAnchor.constraint(equalTo: button.centerYAnchor),
            circle.widthAnchor.constraint(equalToConstant: 30),
            circle.heightAnchor.constraint(equalToConstant: 30)
        ])
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    @objc private func tapped() {
        onToggle?()
    }

    private static func makeSubtitle(_ habit: Habit) -> UIView {
        guard habit.streak > 0 else {
            return makeLabel("No streak yet", size: 13, color: Theme.textTertiary)
        }
        let star = UIImageView(image: Icons.image("star", size: 12))
        star.translatesAutoresizingMaskIntoConstraints = false
        star.tintColor = Theme.gold
        star.widthAnchor.constraint(equalToConstant: 12).isActive = true
        star.heightAnchor.constraint(equalToConstant: 12).isActive = true
        let label = makeLabel("\(habit.streak) day streak", size: 13, color: Theme.gold)
        let stack = UIStackView(arrangedSubviews: [star, label])
        stack.translatesAutoresizingMaskIntoConstraints = false
        stack.axis = .horizontal
        stack.alignment = .center
        stack.spacing = 4
        return stack
    }
}

// MARK: - Statistics: streak row

/// 57pt row: 1pt top divider · 36pt tile · name · streak / best.
final class StreakRowView: UIView {
    init(habit: Habit) {
        super.init(frame: .zero)
        translatesAutoresizingMaskIntoConstraints = false

        let divider = UIView()
        divider.translatesAutoresizingMaskIntoConstraints = false
        divider.backgroundColor = Theme.separator

        let tile = IconTileView()
        tile.translatesAutoresizingMaskIntoConstraints = false
        tile.configure(icon: habit.icon, iconSize: 20)

        let name = makeLabel(habit.name, size: 15, weight: .semibold)
        let value = makeLabel("\(habit.streak)", size: 17, weight: .bold, color: Theme.green)
        let best = makeLabel("Best: \(habit.bestStreak)", size: 11, color: Theme.textTertiary)
        let right = UIStackView(arrangedSubviews: [value, best])
        right.translatesAutoresizingMaskIntoConstraints = false
        right.axis = .vertical
        right.alignment = .trailing
        right.setContentHuggingPriority(.required, for: .horizontal)
        right.setContentCompressionResistancePriority(.required, for: .horizontal)

        addSubview(divider)
        addSubview(tile)
        addSubview(name)
        addSubview(right)

        NSLayoutConstraint.activate([
            heightAnchor.constraint(equalToConstant: 57),

            divider.topAnchor.constraint(equalTo: topAnchor),
            divider.leadingAnchor.constraint(equalTo: leadingAnchor),
            divider.trailingAnchor.constraint(equalTo: trailingAnchor),
            divider.heightAnchor.constraint(equalToConstant: 1),

            tile.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 14),
            tile.topAnchor.constraint(equalTo: topAnchor, constant: 11),
            tile.widthAnchor.constraint(equalToConstant: 36),
            tile.heightAnchor.constraint(equalToConstant: 36),

            name.leadingAnchor.constraint(equalTo: tile.trailingAnchor, constant: 12),
            name.centerYAnchor.constraint(equalTo: tile.centerYAnchor),
            name.trailingAnchor.constraint(lessThanOrEqualTo: right.leadingAnchor, constant: -12),

            right.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -14),
            right.centerYAnchor.constraint(equalTo: tile.centerYAnchor)
        ])
    }

    /// Empty state with the same footprint.
    init(emptyMessage: String) {
        super.init(frame: .zero)
        translatesAutoresizingMaskIntoConstraints = false
        let label = makeLabel(emptyMessage, size: 15, color: Theme.textTertiary)
        addSubview(label)
        NSLayoutConstraint.activate([
            heightAnchor.constraint(equalToConstant: 57),
            label.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 14),
            label.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// MARK: - Statistics: badge

/// 64pt rounded badge tile + title + "Earned" / "Locked".
final class BadgeView: UIView {
    init(title: String, earned: Bool) {
        super.init(frame: .zero)
        translatesAutoresizingMaskIntoConstraints = false

        let tile = IconTileView()
        tile.translatesAutoresizingMaskIntoConstraints = false
        if earned {
            tile.configure(icon: "star", iconSize: 28, radius: 16,
                           background: Theme.tile, tint: Theme.gold)
        } else {
            tile.configure(icon: "lock", iconSize: 26, radius: 16,
                           background: .clear, tint: Theme.textTertiary,
                           dash: Theme.outline, dashWidth: 1)
        }

        let name = makeLabel(title, size: 13, weight: .semibold)
        name.textAlignment = .center
        let status = makeLabel(earned ? "Earned" : "Locked", size: 11, color: Theme.textTertiary)
        status.textAlignment = .center

        let stack = UIStackView(arrangedSubviews: [tile, name, status])
        stack.translatesAutoresizingMaskIntoConstraints = false
        stack.axis = .vertical
        stack.alignment = .center
        stack.spacing = 0
        stack.setCustomSpacing(6, after: tile)
        addSubview(stack)

        NSLayoutConstraint.activate([
            tile.widthAnchor.constraint(equalToConstant: 64),
            tile.heightAnchor.constraint(equalToConstant: 64),
            stack.topAnchor.constraint(equalTo: topAnchor),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor)
        ])
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// MARK: - Statistics: 4-week activity heat-map

struct HeatCell {
    let level: Int        // 0...4
    let isFuture: Bool
    let isToday: Bool
}

/// 32pt cells on a 36pt pitch, weekday header, "W1…W4" row labels and a Less/More legend.
final class HeatmapView: UIView {
    static func level(for ratio: Double) -> Int {
        if ratio <= 0 { return 0 }
        if ratio <= 0.4 + 0.001 { return 1 }
        if ratio <= 0.6 + 0.001 { return 2 }
        if ratio < 1 - 0.001 { return 3 }
        return 4
    }

    static func color(level: Int) -> UIColor {
        switch level {
        case 1: return Theme.accent.withAlphaComponent(0.3)
        case 2: return Theme.accent.withAlphaComponent(0.6)
        case 3: return Theme.accent.withAlphaComponent(0.85)
        case 4: return Theme.accent
        default: return Theme.tile
        }
    }

    private let cell: CGFloat = 32
    private let pitch: CGFloat = 36
    private let gridLeft: CGFloat = 28
    private let headerHeight: CGFloat = 13

    private var gridViews: [UIView] = []
    private let lessLabel = makeLabel("Less", size: 11, color: Theme.textTertiary)
    private let moreLabel = makeLabel("More", size: 11, color: Theme.textTertiary)
    private var legendSquares: [UIView] = []

    override init(frame: CGRect) {
        super.init(frame: frame)
        setup()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setup()
    }

    private func setup() {
        for label in [lessLabel, moreLabel] {
            label.translatesAutoresizingMaskIntoConstraints = true
            addSubview(label)
        }
        for level in 0...4 {
            let square = UIView()
            square.backgroundColor = HeatmapView.color(level: level)
            square.layer.cornerRadius = 3
            addSubview(square)
            legendSquares.append(square)
        }
    }

    func configure(weeks: [[HeatCell]]) {
        gridViews.forEach { $0.removeFromSuperview() }
        gridViews = []

        let letters = ["M", "T", "W", "T", "F", "S", "S"]
        for (i, letter) in letters.enumerated() {
            let label = makeLabel(letter, size: 11, color: Theme.textTertiary)
            label.translatesAutoresizingMaskIntoConstraints = true
            label.textAlignment = .center
            label.frame = CGRect(x: gridLeft + CGFloat(i) * pitch, y: 0, width: cell, height: headerHeight)
            addSubview(label)
            gridViews.append(label)
        }

        let gridTop = headerHeight + 6
        for (row, week) in weeks.enumerated() {
            let y = gridTop + CGFloat(row) * pitch

            let rowLabel = makeLabel("W\(row + 1)", size: 11, color: Theme.textTertiary)
            rowLabel.translatesAutoresizingMaskIntoConstraints = true
            rowLabel.frame = CGRect(x: 0, y: y, width: 24, height: cell)
            addSubview(rowLabel)
            gridViews.append(rowLabel)

            for (col, item) in week.enumerated() {
                let view = UIView(frame: CGRect(x: gridLeft + CGFloat(col) * pitch, y: y, width: cell, height: cell))
                view.layer.cornerRadius = 6
                if item.isFuture {
                    let dash = CAShapeLayer()
                    dash.frame = view.bounds
                    dash.fillColor = UIColor.clear.cgColor
                    dash.strokeColor = Theme.outline.cgColor
                    dash.lineWidth = 1
                    dash.lineDashPattern = [3, 3]
                    dash.path = UIBezierPath(roundedRect: view.bounds.insetBy(dx: 0.5, dy: 0.5), cornerRadius: 5.5).cgPath
                    view.layer.addSublayer(dash)
                } else {
                    view.backgroundColor = HeatmapView.color(level: item.level)
                    if item.isToday {
                        view.layer.borderWidth = 1.5
                        view.layer.borderColor = Theme.currentDay.cgColor
                    }
                }
                addSubview(view)
                gridViews.append(view)
            }
        }
        setNeedsLayout()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        // Legend is right-aligned, 4pt gaps, extra 4pt margin beside the captions.
        let legendY = headerHeight + 6 + 4 * pitch - 4 + 12
        lessLabel.sizeToFit()
        moreLabel.sizeToFit()
        var x = bounds.width - moreLabel.bounds.width
        moreLabel.frame = CGRect(x: x, y: legendY, width: moreLabel.bounds.width, height: 13)
        x -= 8
        for square in legendSquares.reversed() {
            x -= 12
            square.frame = CGRect(x: x, y: legendY + 0.5, width: 12, height: 12)
            x -= 4
        }
        x += 4 - 8
        lessLabel.frame = CGRect(x: x - lessLabel.bounds.width, y: legendY, width: lessLabel.bounds.width, height: 13)
    }
}
