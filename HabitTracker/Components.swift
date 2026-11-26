import UIKit

// MARK: - Label with design letter-spacing / line-height

/// UILabel that supports CSS-style `letter-spacing` (kern) and `line-height`.
/// Both are inspectable so they can be set straight from the storyboard.
final class HTLabel: UILabel {
    @IBInspectable var kern: CGFloat = 0 { didSet { applyStyle() } }
    @IBInspectable var lineHeight: CGFloat = 0 { didSet { applyStyle() } }

    override var text: String? {
        didSet { applyStyle() }
    }

    override func awakeFromNib() {
        super.awakeFromNib()
        applyStyle()
    }

    private func applyStyle() {
        guard kern != 0 || lineHeight != 0 else { return }
        guard let string = text, !string.isEmpty else { return }
        let currentFont: UIFont = font
        let currentColor: UIColor = textColor
        var attributes: [NSAttributedString.Key: Any] = [
            .font: currentFont,
            .foregroundColor: currentColor
        ]
        if kern != 0 { attributes[.kern] = kern }
        let paragraph = NSMutableParagraphStyle()
        paragraph.alignment = textAlignment
        paragraph.lineBreakMode = lineBreakMode
        if lineHeight != 0 {
            paragraph.minimumLineHeight = lineHeight
            paragraph.maximumLineHeight = lineHeight
            attributes[.baselineOffset] = (lineHeight - currentFont.lineHeight) / 4
        }
        attributes[.paragraphStyle] = paragraph
        attributedText = NSAttributedString(string: string, attributes: attributes)
    }
}

// MARK: - Buttons

/// Base button: dims while pressed (like the design's pressable controls).
class HTButton: UIButton {
    override var isHighlighted: Bool {
        didSet { alpha = isHighlighted ? 0.6 : 1 }
    }
}

/// Navigation-row button: optional vector icon (`iconName`) + optional title,
/// tinted #8B7BFF, 17pt regular — exactly the design's `.nb` control.
final class NavButton: HTButton {
    @IBInspectable var iconName: String = ""
    @IBInspectable var iconStroke: CGFloat = 1.7

    override func awakeFromNib() {
        super.awakeFromNib()
        var config = UIButton.Configuration.plain()
        config.contentInsets = .zero
        config.imagePadding = 2
        config.baseForegroundColor = Theme.navTint
        if let title = title(for: .normal), !title.isEmpty {
            var attributed = AttributedString(title)
            attributed.font = Theme.font(17)
            config.attributedTitle = attributed
        }
        if !iconName.isEmpty {
            config.image = Icons.image(iconName, size: 24, stroke: iconStroke)
        }
        configuration = config
    }
}

// MARK: - Progress bar

/// 6pt rounded progress bar: #252540 track, #6C63FF fill.
final class ProgressBarView: UIView {
    @IBInspectable var progress: CGFloat = 0.6 { didSet { updateFill() } }
    private let fill = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setup()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setup()
    }

    private func setup() {
        backgroundColor = Theme.tile
        layer.cornerRadius = 3
        clipsToBounds = true
        fill.backgroundColor = Theme.accent
        addSubview(fill)
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        updateFill()
    }

    private func updateFill() {
        let p = min(max(progress, 0), 1)
        fill.frame = CGRect(x: 0, y: 0, width: bounds.width * p, height: bounds.height)
    }

    func setProgress(_ value: CGFloat, animated: Bool, duration: TimeInterval = 0.6) {
        if animated {
            UIView.animate(withDuration: duration, delay: 0, options: [.curveEaseInOut]) {
                self.progress = value
            }
        } else {
            progress = value
        }
    }
}

// MARK: - Icon tile

/// Rounded tile with a centred vector icon; optional dashed border.
final class IconTileView: UIView {
    private let imageView = UIImageView()
    private let dashLayer = CAShapeLayer()
    private var iconSize: CGFloat = 22
    private var cornerRadiusValue: CGFloat = 10
    private var dashWidth: CGFloat = 0

    override init(frame: CGRect) {
        super.init(frame: frame)
        setup()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setup()
    }

    private func setup() {
        isUserInteractionEnabled = false
        backgroundColor = Theme.tile
        imageView.contentMode = .center
        imageView.tintColor = Theme.icon
        addSubview(imageView)
        dashLayer.fillColor = UIColor.clear.cgColor
        dashLayer.isHidden = true
        layer.addSublayer(dashLayer)
    }

    func configure(icon: String,
                   iconSize: CGFloat,
                   radius: CGFloat = 10,
                   background: UIColor = Theme.tile,
                   tint: UIColor = Theme.icon,
                   stroke: CGFloat = 1.7,
                   dash: UIColor? = nil,
                   dashWidth: CGFloat = 1) {
        self.iconSize = iconSize
        self.cornerRadiusValue = radius
        self.dashWidth = dashWidth
        layer.cornerRadius = radius
        backgroundColor = background
        imageView.tintColor = tint
        imageView.image = Icons.image(icon, size: iconSize, stroke: stroke)
        if let dash = dash {
            dashLayer.isHidden = false
            dashLayer.strokeColor = dash.cgColor
            dashLayer.lineWidth = dashWidth
            dashLayer.lineDashPattern = [NSNumber(value: Double(dashWidth * 3)), NSNumber(value: Double(dashWidth * 3))]
        } else {
            dashLayer.isHidden = true
        }
        setNeedsLayout()
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        imageView.frame = bounds
        let inset = dashWidth / 2
        dashLayer.frame = bounds
        dashLayer.path = UIBezierPath(roundedRect: bounds.insetBy(dx: inset, dy: inset),
                                      cornerRadius: max(cornerRadiusValue - inset, 0)).cgPath
    }
}

// MARK: - Text field

/// 48pt input: #1A1A2E fill, 1pt #333350 border, 12pt radius, 14pt side padding.
final class PaddedTextField: UITextField {
    override func awakeFromNib() {
        super.awakeFromNib()
        backgroundColor = Theme.card
        textColor = .white
        tintColor = Theme.accent
        keyboardAppearance = .dark
        layer.cornerRadius = 12
        layer.borderWidth = 1
        layer.borderColor = Theme.fieldBorder.cgColor
        attributedPlaceholder = NSAttributedString(
            string: placeholder ?? "",
            attributes: [.foregroundColor: Theme.textTertiary])
    }

    private func padded(_ rect: CGRect) -> CGRect {
        return rect.insetBy(dx: 14, dy: 0)
    }

    override func textRect(forBounds bounds: CGRect) -> CGRect { return padded(bounds) }
    override func editingRect(forBounds bounds: CGRect) -> CGRect { return padded(bounds) }
    override func placeholderRect(forBounds bounds: CGRect) -> CGRect { return padded(bounds) }
}

// MARK: - Convenience

extension UIView {
    /// Adds a subview and pins it to the edges (or insets) of this view.
    func pin(_ child: UIView, insets: UIEdgeInsets = .zero) {
        child.translatesAutoresizingMaskIntoConstraints = false
        addSubview(child)
        NSLayoutConstraint.activate([
            child.topAnchor.constraint(equalTo: topAnchor, constant: insets.top),
            child.leadingAnchor.constraint(equalTo: leadingAnchor, constant: insets.left),
            child.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -insets.right),
            child.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -insets.bottom)
        ])
    }
}

func makeLabel(_ text: String = "", size: CGFloat, weight: UIFont.Weight = .regular, color: UIColor = .white) -> UILabel {
    let label = UILabel()
    label.translatesAutoresizingMaskIntoConstraints = false
    label.text = text
    label.font = Theme.font(size, weight)
    label.textColor = color
    return label
}
