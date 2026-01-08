"""
Test script for enterprise improvements.
Tests: Field Validation, Fallback Metadata, Structured Logging
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("🧪 ENTERPRISE IMPROVEMENTS TEST SUITE")
print("=" * 60)

# Test 1: Field Validation - Valid Review
print("\n1️⃣ TEST: Valid Review Fields")
response = requests.post(f"{API_URL}/generate-description", json={
    "entity_type": "review",
    "generation_mode": "template",
    "fields": {
        "name": "Phase 1 Inspection",
        "start_date": "2026-01-05",
        "due_date": "2026-01-15",
        "workflow": "Approval Workflow",
        "priority": "High"
    }
})
print(f"Status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"✅ Description generated: {data['generated_description'][:50]}...")
    print(f"✅ Metadata: {json.dumps(data.get('metadata'), indent=2)}")
else:
    print(f"❌ Error: {response.text}")

# Test 2: Field Validation - Missing Required Field
print("\n2️⃣ TEST: Missing Required Field (name)")
response = requests.post(f"{API_URL}/generate-description", json={
    "entity_type": "review",
    "generation_mode": "template",
    "fields": {
        "start_date": "2026-01-05",
        "due_date": "2026-01-15",
        "workflow": "Approval Workflow",
        "priority": "High"
    }
})
print(f"Status: {response.status_code}")
if response.status_code == 422:
    print("✅ Correctly rejected missing field")
    print(f"Error: {response.json()['detail'][0]['msg']}")
else:
    print(f"❌ Should have failed validation, got: {response.status_code}")

# Test 3: AI Fallback Metadata
print("\n3️⃣ TEST: AI Mode with Fallback Metadata")
response = requests.post(f"{API_URL}/generate-description", json={
    "entity_type": "review",
    "generation_mode": "ai",
    "fields": {
        "name": "Safety Inspection",
        "start_date": "2026-02-01",
        "due_date": "2026-02-10",
        "workflow": "Safety Review",
        "priority": "Critical"
    }
})
print(f"Status: {response.status_code}")
if response.ok:
    data = response.json()
    metadata = data.get('metadata', {})
    print(f"✅ Mode requested: {metadata.get('mode_requested')}")
    print(f"✅ Mode used: {metadata.get('mode_used')}")
    print(f"✅ Fallback used: {metadata.get('fallback_used')}")
    if metadata.get('fallback_used'):
        print(f"✅ Fallback reason: {metadata.get('fallback_reason')}")
    print(f"✅ Provider: {metadata.get('provider')}")
    print(f"✅ Latency: {metadata.get('latency_ms')}ms")
else:
    print(f"❌ Error: {response.text}")

# Test 4: RFA Fields
print("\n4️⃣ TEST: RFA with Required Fields")
response = requests.post(f"{API_URL}/generate-description", json={
    "entity_type": "rfa",
    "generation_mode": "template",
    "fields": {
        "name": "Material Approval",
        "request_date": "2026-01-10",
        "due_date": "2026-01-20",
        "workflow": "Procurement",
        "priority": "Medium"
    }
})
print(f"Status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"✅ Description: {data['generated_description'][:60]}...")
    print(f"✅ Latency: {data['metadata']['latency_ms']}ms")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED")
print("=" * 60)
