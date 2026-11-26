import UIKit

/// Design tokens lifted 1:1 from the Habit Tracker iOS UI design file.
enum Theme {
    static func hex(_ value: UInt32, alpha: CGFloat = 1) -> UIColor {
        return UIColor(red: CGFloat((value >> 16) & 0xFF) / 255,
                       green: CGFloat((value >> 8) & 0xFF) / 255,
                       blue: CGFloat(value & 0xFF) / 255,
                       alpha: alpha)
    }

    static let background    = hex(0x0F0F15)
    static let card          = hex(0x1A1A2E)
    static let tile          = hex(0x252540)
    static let accent        = hex(0x6C63FF)
    static let navTint       = hex(0x8B7BFF)
    static let icon          = hex(0xB77BF5)
    static let textSecondary = hex(0xB0B0C0)
    static let textTertiary  = hex(0x8A8AA3)
    static let gold          = hex(0xF59E0B)
    static let green         = hex(0x34D399)
    static let pink          = hex(0xF472B6)
    static let red           = hex(0xF87171)
    static let outline       = hex(0x4A4A6A)
    static let fieldBorder   = hex(0x333350)
    static let daySelected   = hex(0x2E2E4A)
    static let separator     = hex(0x262640)
    static let currentDay    = hex(0xA855F7)

    static func font(_ size: CGFloat, _ weight: UIFont.Weight = .regular) -> UIFont {
        return UIFont.systemFont(ofSize: size, weight: weight)
    }
}
