import UIKit

/// Draws the design's vector icons (24x24 grid, round caps/joins) as template images.
enum Icons {
    private static var cache: [String: UIImage] = [:]

    /// - Parameters:
    ///   - size: rendered point size (the 24pt grid is scaled to this)
    ///   - stroke: stroke width in the 24-unit grid (design default is 1.7)
    static func image(_ name: String, size: CGFloat, stroke: CGFloat = 1.7) -> UIImage? {
        let key = "\(name)|\(size)|\(stroke)"
        if let hit = cache[key] { return hit }
        guard let data = IconData.paths[name] else { return nil }

        let path = makePath(data)
        path.lineWidth = stroke
        path.lineCapStyle = .round
        path.lineJoinStyle = .round
        let isFilled = IconData.filled.contains(name)

        let renderer = UIGraphicsImageRenderer(size: CGSize(width: size, height: size))
        let image = renderer.image { context in
            context.cgContext.scaleBy(x: size / 24, y: size / 24)
            UIColor.black.setStroke()
            UIColor.black.setFill()
            if isFilled { path.fill() }
            path.stroke()
        }.withRenderingMode(.alwaysTemplate)
        cache[key] = image
        return image
    }

    private static func makePath(_ d: String) -> UIBezierPath {
        let path = UIBezierPath()
        let t = d.split(separator: " ").map(String.init)
        var i = 0
        func num() -> CGFloat {
            let v = CGFloat(Double(t[i]) ?? 0)
            i += 1
            return v
        }
        while i < t.count {
            let cmd = t[i]
            i += 1
            switch cmd {
            case "M":
                let x = num(); let y = num()
                path.move(to: CGPoint(x: x, y: y))
            case "L":
                let x = num(); let y = num()
                path.addLine(to: CGPoint(x: x, y: y))
            case "C":
                let x1 = num(); let y1 = num()
                let x2 = num(); let y2 = num()
                let x = num(); let y = num()
                path.addCurve(to: CGPoint(x: x, y: y),
                              controlPoint1: CGPoint(x: x1, y: y1),
                              controlPoint2: CGPoint(x: x2, y: y2))
            case "Z":
                path.close()
            default:
                break
            }
        }
        return path
    }
}
