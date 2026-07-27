import HealthKit

// Keep this feature behind a build flag and a purpose-specific consent screen.
final class HealthImporter {
    let store = HKHealthStore()
    func requestReadAuthorization(for types: Set<HKObjectType>) async throws {
        try await store.requestAuthorization(toShare: [], read: types)
        // HealthKit intentionally does not disclose whether read authorization was granted.
        // Execute a bounded query and handle an empty result without presenting it as denial.
    }
    func stepCountType() -> HKQuantityType? { HKQuantityType.quantityType(forIdentifier: .stepCount) }
}
