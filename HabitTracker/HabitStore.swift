import Foundation

extension Notification.Name {
    static let habitStoreChanged = Notification.Name("HabitTracker.storeChanged")
}

/// "yyyy-MM-dd" keys in the user's current time zone.
enum DateKey {
    private static let formatter: DateFormatter = {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    static func string(_ date: Date) -> String { return formatter.string(from: date) }
    static func date(_ key: String) -> Date? { return formatter.date(from: key) }
}

struct Habit: Codable, Equatable {
    var id: String
    var name: String
    var icon: String
    /// Monday ... Sunday
    var days: [Bool]
    var streak: Int
    var bestStreak: Int
    /// Date key of the most recent check-in.
    var lastDone: String?
}

struct BadgeInfo {
    let id: String
    let title: String
}

struct AppState: Codable {
    var habits: [Habit]
    var xp: Int
    var dayStreak: Int
    var lastActive: String?
    var perfectDate: String?
    var badges: [String]
    var totalCheckIns: Int
    /// Completion ratio (0...1) for finished days.
    var activity: [String: Double]
    var todayDate: String
    var todayRatio: Double
}

/// Single source of truth. Persists to UserDefaults and posts `.habitStoreChanged`.
///
/// Rules (from the "How rewards work" screen):
///  • +10 XP per check-in (taken back when un-checked)
///  • +20 XP perfect-day bonus, once per day
///  • level = xp / 100 + 1
///  • streaks only count days a habit is scheduled
///  • badges are earned once
final class HabitStore {
    static let shared = HabitStore()

    static let xpPerCheckIn = 10
    static let perfectDayBonus = 20
    static let xpPerLevel = 100
    private static let storageKey = "habit.tracker.state.v1"

    static let badgeDefinitions: [BadgeInfo] = [
        BadgeInfo(id: "first", title: "First Check-in"),
        BadgeInfo(id: "streak3", title: "3-Day Streak"),
        BadgeInfo(id: "perfect", title: "Perfect Day"),
        BadgeInfo(id: "streak7", title: "7-Day Streak"),
        BadgeInfo(id: "checkins50", title: "50 Check-ins"),
        BadgeInfo(id: "level5", title: "Level 5")
    ]

    private(set) var state: AppState

    private init() {
        if let data = UserDefaults.standard.data(forKey: HabitStore.storageKey),
           let saved = try? JSONDecoder().decode(AppState.self, from: data) {
            state = saved
        } else {
            state = HabitStore.makeSeed(today: Date())
        }
        rollOver()
    }

    // MARK: Calendar helpers

    private var calendar: Calendar { return Calendar(identifier: .gregorian) }

    /// 0 = Monday ... 6 = Sunday
    func weekdayIndex(_ date: Date) -> Int {
        return (calendar.component(.weekday, from: date) + 5) % 7
    }

    // MARK: Queries

    var habits: [Habit] { return state.habits }

    func scheduledToday(now: Date = Date()) -> [Habit] {
        let index = weekdayIndex(now)
        return state.habits.filter { $0.days.count == 7 && $0.days[index] }
    }

    func isDone(_ habit: Habit, now: Date = Date()) -> Bool {
        return habit.lastDone == DateKey.string(now)
    }

    func doneCount(now: Date = Date()) -> Int {
        return scheduledToday(now: now).filter { isDone($0, now: now) }.count
    }

    var xp: Int { return state.xp }
    var level: Int { return state.xp / HabitStore.xpPerLevel + 1 }
    var xpToNextLevel: Int { return HabitStore.xpPerLevel - state.xp % HabitStore.xpPerLevel }
    var levelProgress: Double { return Double(state.xp % HabitStore.xpPerLevel) / Double(HabitStore.xpPerLevel) }
    var dayStreak: Int { return state.dayStreak }
    var bestStreak: Int { return state.habits.map { $0.bestStreak }.max() ?? 0 }

    func isBadgeEarned(_ id: String) -> Bool { return state.badges.contains(id) }

    /// Completion ratio for a day (live for today, recorded for past days).
    func ratio(on date: Date, now: Date = Date()) -> Double {
        let key = DateKey.string(date)
        if key == DateKey.string(now) { return liveRatio(now: now) }
        return state.activity[key] ?? 0
    }

    /// Mean daily completion over the last 7 days (today included).
    func weekRate(now: Date = Date()) -> Double {
        var total = 0.0
        for offset in 0..<7 {
            if let day = calendar.date(byAdding: .day, value: -offset, to: now) {
                total += ratio(on: day, now: now)
            }
        }
        return total / 7
    }

    private func liveRatio(now: Date) -> Double {
        let scheduled = scheduledToday(now: now)
        guard !scheduled.isEmpty else { return 0 }
        let done = scheduled.filter { isDone($0, now: now) }.count
        return Double(done) / Double(scheduled.count)
    }

    // MARK: Mutations

    func toggle(habitId: String, now: Date = Date()) {
        rollOver(now: now)
        guard let index = state.habits.firstIndex(where: { $0.id == habitId }) else { return }
        let todayKey = DateKey.string(now)
        let yesterdayKey = calendar.date(byAdding: .day, value: -1, to: now).map { DateKey.string($0) }
        var habit = state.habits[index]

        if habit.lastDone == todayKey {
            // Un-check: take the XP back.
            habit.streak = max(0, habit.streak - 1)
            habit.lastDone = habit.streak > 0 ? yesterdayKey : nil
            state.habits[index] = habit
            state.xp = max(0, state.xp - HabitStore.xpPerCheckIn)
            state.totalCheckIns = max(0, state.totalCheckIns - 1)

            let scheduled = scheduledToday(now: now)
            let allDone = !scheduled.isEmpty && scheduled.allSatisfy { isDone($0, now: now) }
            if state.perfectDate == todayKey && !allDone {
                state.xp = max(0, state.xp - HabitStore.perfectDayBonus)
                state.perfectDate = nil
            }
            if doneCount(now: now) == 0 && state.lastActive == todayKey {
                state.dayStreak = max(0, state.dayStreak - 1)
                state.lastActive = state.dayStreak > 0 ? yesterdayKey : nil
            }
        } else {
            // Check in.
            habit.streak += 1
            habit.bestStreak = max(habit.bestStreak, habit.streak)
            habit.lastDone = todayKey
            state.habits[index] = habit
            state.xp += HabitStore.xpPerCheckIn
            state.totalCheckIns += 1

            if state.lastActive != todayKey {
                state.dayStreak = (state.lastActive == yesterdayKey) ? state.dayStreak + 1 : 1
                state.lastActive = todayKey
            }

            award("first")
            if habit.streak >= 3 { award("streak3") }
            if habit.streak >= 7 { award("streak7") }
            if state.totalCheckIns >= 50 { award("checkins50") }

            let scheduled = scheduledToday(now: now)
            let allDone = !scheduled.isEmpty && scheduled.allSatisfy { isDone($0, now: now) }
            if allDone && state.perfectDate != todayKey {
                state.xp += HabitStore.perfectDayBonus
                state.perfectDate = todayKey
                award("perfect")
            }
            if level >= 5 { award("level5") }
        }

        state.todayRatio = liveRatio(now: now)
        persist(notify: true)
    }

    func addHabit(name: String, icon: String, days: [Bool]) {
        let habit = Habit(id: UUID().uuidString, name: name, icon: icon, days: days,
                          streak: 0, bestStreak: 0, lastDone: nil)
        state.habits.append(habit)
        state.todayRatio = liveRatio(now: Date())
        persist(notify: true)
    }

    private func award(_ id: String) {
        if !state.badges.contains(id) { state.badges.append(id) }
    }

    // MARK: Day roll-over

    /// Archives yesterday, breaks streaks for missed scheduled days.
    func rollOver(now: Date = Date()) {
        let todayKey = DateKey.string(now)
        var dirty = false

        if state.todayDate != todayKey {
            state.activity[state.todayDate] = state.todayRatio
            state.todayDate = todayKey
            dirty = true
        }

        for index in state.habits.indices {
            if state.habits[index].streak > 0 && isStreakBroken(state.habits[index], now: now) {
                state.habits[index].streak = 0
                dirty = true
            }
        }

        if state.dayStreak > 0, let last = state.lastActive, last != todayKey,
           let lastDate = DateKey.date(last) {
            let gap = calendar.dateComponents([.day], from: lastDate, to: calendar.startOfDay(for: now)).day ?? 0
            if gap > 1 {
                state.dayStreak = 0
                dirty = true
            }
        }

        let ratio = liveRatio(now: now)
        if state.todayRatio != ratio {
            state.todayRatio = ratio
            dirty = true
        }
        if dirty { persist(notify: false) }
    }

    private func isStreakBroken(_ habit: Habit, now: Date) -> Bool {
        guard let last = habit.lastDone, let lastDate = DateKey.date(last) else { return true }
        let todayStart = calendar.startOfDay(for: now)
        guard var day = calendar.date(byAdding: .day, value: 1, to: lastDate) else { return false }
        while day < todayStart {
            if habit.days.count == 7 && habit.days[weekdayIndex(day)] { return true }
            guard let next = calendar.date(byAdding: .day, value: 1, to: day) else { break }
            day = next
        }
        return false
    }

    // MARK: Persistence

    private func persist(notify: Bool) {
        if let data = try? JSONEncoder().encode(state) {
            UserDefaults.standard.set(data, forKey: HabitStore.storageKey)
        }
        if notify {
            NotificationCenter.default.post(name: .habitStoreChanged, object: self)
        }
    }

    // MARK: Demo data

    /// First-launch data. Reproduces the design's numbers exactly:
    /// 240 XP / Level 3, 5-day streak, 3 of 5 done, streaks 12·5·8·3,
    /// best streak 21, and the 4-week activity grid (This Week = 71%).
    private static func makeSeed(today: Date) -> AppState {
        let calendar = Calendar(identifier: .gregorian)
        let todayKey = DateKey.string(today)
        let yesterday = calendar.date(byAdding: .day, value: -1, to: today) ?? today
        let yesterdayKey = DateKey.string(yesterday)
        let everyDay = [Bool](repeating: true, count: 7)

        let habits = [
            Habit(id: "seed-run", name: "Morning Run", icon: "run", days: everyDay,
                  streak: 12, bestStreak: 21, lastDone: todayKey),
            Habit(id: "seed-read", name: "Read 30min", icon: "read", days: everyDay,
                  streak: 0, bestStreak: 0, lastDone: nil),
            Habit(id: "seed-water", name: "Drink Water", icon: "water", days: everyDay,
                  streak: 5, bestStreak: 9, lastDone: todayKey),
            Habit(id: "seed-gym", name: "Gym", icon: "gym", days: everyDay,
                  streak: 3, bestStreak: 10, lastDone: yesterdayKey),
            Habit(id: "seed-meditate", name: "Meditate", icon: "meditate", days: everyDay,
                  streak: 8, bestStreak: 14, lastDone: todayKey)
        ]

        // Oldest -> newest, ending on "yesterday" (22 values = W1…W3 + Monday of W4).
        let pattern: [Double] = [
            0.6, 0.8, 1.0, 1.0, 0.8, 0.2, 0.0,
            0.8, 1.0, 1.0, 0.8, 1.0, 0.6, 0.2,
            1.0, 1.0, 0.8, 1.0, 1.0, 0.6, 0.0,
            1.0
        ]
        var activity: [String: Double] = [:]
        for back in 1...34 {
            guard let day = calendar.date(byAdding: .day, value: -back, to: today) else { continue }
            let slot = (((pattern.count - back) % pattern.count) + pattern.count) % pattern.count
            activity[DateKey.string(day)] = pattern[slot]
        }

        return AppState(habits: habits,
                        xp: 240,
                        dayStreak: 5,
                        lastActive: todayKey,
                        perfectDate: nil,
                        badges: ["first", "streak3", "perfect"],
                        totalCheckIns: 41,
                        activity: activity,
                        todayDate: todayKey,
                        todayRatio: 0.6)
    }
}
