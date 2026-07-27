import Photos
import PhotosUI
import SwiftUI

struct PhotoImporter: View {
    @Binding var selection: [PhotosPickerItem]
    let onExport: ([ExportEnvelope<PhotoPayload>]) -> Void
    var body: some View { PhotosPicker(selection: $selection, maxSelectionCount: 50, matching: .images) { Label("Select photos", systemImage: "photo.on.rectangle") }.onChange(of: selection) { _, items in Task { await export(items) } } }
    @MainActor private func export(_ items: [PhotosPickerItem]) async {
        var rows: [ExportEnvelope<PhotoPayload>] = []
        for item in items {
            // Data is deliberately not inserted into MCP records. Encrypt/store separately only with separate consent.
            guard let data = try? await item.loadTransferable(type: Data.self) else { continue }
            rows.append(.init(id: UUID().uuidString, exportedAt: .now, source: "photos", payload: .init(byteCount: data.count, contentType: item.supportedContentTypes.first?.identifier), consentPurpose: "user-selected Photos picker export"))
        }
        onExport(rows)
    }
}
struct PhotoPayload: Codable { let byteCount: Int; let contentType: String? }
