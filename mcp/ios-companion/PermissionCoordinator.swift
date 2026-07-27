import Contacts
import EventKit
import Photos

@MainActor
final class PermissionCoordinator: ObservableObject {
    enum PermissionError: LocalizedError { case denied(String); var errorDescription: String? { switch self { case .denied(let s): return s } } }
    private let contacts = CNContactStore()
    private let events = EKEventStore()

    func requestPhotos() async throws -> PHAuthorizationStatus {
        let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
        guard status == .authorized || status == .limited else { throw PermissionError.denied("Photos access was not granted.") }
        return status
    }
    func requestContacts() async throws {
        let granted = try await contacts.requestAccess(for: .contacts)
        guard granted else { throw PermissionError.denied("Contacts access was not granted.") }
    }
    func requestCalendars() async throws {
        // iOS 17+: request full access only if your purpose genuinely needs it.
        let granted: Bool
        if #available(iOS 17.0, *) { granted = try await events.requestFullAccessToEvents() }
        else { granted = try await events.requestAccess(to: .event) }
        guard granted else { throw PermissionError.denied("Calendar access was not granted.") }
    }
}
