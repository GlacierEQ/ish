import SwiftUI
import UniformTypeIdentifiers

struct DocumentImporter: UIViewControllerRepresentable {
    let onImported: (Result<[ExportEnvelope<DocumentPayload>], Error>) -> Void
    func makeCoordinator() -> Coordinator { Coordinator(onImported: onImported) }
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.pdf, .plainText, .commaSeparatedText], asCopy: true)
        picker.allowsMultipleSelection = true; picker.delegate = context.coordinator; return picker
    }
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}
    final class Coordinator: NSObject, UIDocumentPickerDelegate {
        let onImported: (Result<[ExportEnvelope<DocumentPayload>], Error>) -> Void
        init(onImported: @escaping (Result<[ExportEnvelope<DocumentPayload>], Error>) -> Void) { self.onImported = onImported }
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            do { onImported(.success(try urls.map(copyAndDescribe))) } catch { onImported(.failure(error)) }
        }
        private func copyAndDescribe(_ url: URL) throws -> ExportEnvelope<DocumentPayload> {
            guard url.startAccessingSecurityScopedResource() else { throw CocoaError(.fileNoPermission) }; defer { url.stopAccessingSecurityScopedResource() }
            let values = try url.resourceValues(forKeys: [.fileSizeKey, .contentTypeKey, .nameKey])
            guard (values.fileSize ?? 0) <= 20 * 1024 * 1024 else { throw CocoaError(.fileWriteFileExists) } // replace with domain-specific error
            // asCopy provides app-managed copy; set completeFileProtection on any retained file.
            return .init(id: UUID().uuidString, exportedAt: .now, source: "document-picker", payload: .init(name: values.name ?? "file", byteCount: values.fileSize ?? 0, contentType: values.contentType?.identifier), consentPurpose: "user-selected file import")
        }
    }
}
struct DocumentPayload: Codable { let name: String; let byteCount: Int; let contentType: String? }
