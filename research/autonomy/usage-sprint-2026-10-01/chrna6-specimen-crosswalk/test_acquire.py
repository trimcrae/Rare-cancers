#!/usr/bin/env python3
"""Synthetic provenance/missing-evidence regression cases; no empirical study claims."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("crosswalk", Path(__file__).with_name("acquire.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def source(key, body):
    raw = json.dumps(body, ensure_ascii=False)
    return {"key": key, "requested_url": m.METADATA[key], "status": "acquired", "http_status": 200,
            "final_url": m.METADATA[key], "robots": {"url": "https://" + m.urllib.parse.urlsplit(m.METADATA[key]).hostname + "/robots.txt", "decision": "allow_missing_robots", "http_status": 404},
            "raw_utf8": raw, "sha256": m.sha(raw.encode()), "bytes": len(raw.encode())}

def fixture():
    epmc = {"resultList": {"result": [{"id": m.PMID, "source": "MED", "doi": m.DOI,
            "title": "Synthetic metadata fixture", "abstractText": "Synthetic 25 EMC text; no patient crosswalk."}]}}
    cr = {"message": {"DOI": m.DOI, "title": ["Synthetic metadata fixture"]}}
    sources = [source("europe_pmc", epmc), source("crossref", cr)]
    return {"schema": "emc-chrna6-specimen-crosswalk/1", "pmid": m.PMID, "doi": m.DOI,
            "scope": "source availability and methods evidence only; no expression analysis, CISH threshold inference or clinical validation",
            "sources": sources, "metadata_projection": m.metadata_fields(sources),
            "adjudication": {"specimen_overlap": "unknown", "patient_overlap": "unknown", "crosswalk_status": "not_established",
              "independent_validation": "not_established",
              "reason": "No reviewed specimen/patient crosswalk binds the CHRNA6 discovery/validation study to the existing GEO cohort. Accessible abstract or link metadata alone cannot adjudicate reuse."}}

class Integrity(unittest.TestCase):
    def setUp(self):
        self.r = fixture()
    def bad(self):
        with self.assertRaises((ValueError, KeyError, TypeError, json.JSONDecodeError)):
            m.validate(self.r)
    def test_valid_raw_bindings(self):
        self.assertEqual(len(m.validate(self.r)), 2)
    def test_blocked_source_retains_unknown(self):
        self.r["sources"] = [{"key": k, "requested_url": u, "status": "http_unavailable", "http_status": 403,
           "robots": {"url": "https://" + m.urllib.parse.urlsplit(u).hostname + "/robots.txt", "decision": "allow_missing_robots", "http_status": 404}} for k, u in m.METADATA.items()]
        self.r["metadata_projection"] = {}
        self.assertEqual(m.validate(self.r), {})
    def test_changed_raw_hash(self):
        self.r["sources"][0]["raw_utf8"] += " "
        self.bad()
    def test_changed_raw_size(self):
        self.r["sources"][0]["bytes"] += 1
        self.bad()
    def test_record_doi_mismatch(self):
        self.r["doi"] = "10.123/other"
        self.bad()
    def test_same_size_wrong_doi_in_source(self):
        raw = self.r["sources"][0]["raw_utf8"].replace(m.DOI, "10.1016/j.modpat.2024.100465")
        self.r["sources"][0].update(raw_utf8=raw, bytes=len(raw.encode()), sha256=m.sha(raw.encode()))
        self.bad()
    def test_duplicate_matching_primary_records(self):
        body = json.loads(self.r["sources"][0]["raw_utf8"])
        body["resultList"]["result"] *= 2
        self.r["sources"][0] = source("europe_pmc", body)
        self.bad()
    def test_wrong_primary_source(self):
        body = json.loads(self.r["sources"][0]["raw_utf8"])
        body["resultList"]["result"][0]["source"] = "PMC"
        self.r["sources"][0] = source("europe_pmc", body)
        self.bad()
    def test_wrong_crossref_doi(self):
        self.r["sources"][1] = source("crossref", {"message": {"DOI": "10.123/other"}})
        self.bad()
    def test_reconstructed_projection_diverges(self):
        self.r["metadata_projection"]["europe_pmc"]["abstractText"] += " independent"
        self.bad()
    def test_unsupported_independence(self):
        self.r["adjudication"]["independent_validation"] = "established"
        self.bad()
    def test_absence_is_not_unknown(self):
        self.r["adjudication"]["specimen_overlap"] = "none"
        self.bad()
    def test_duplicates_cannot_inflate_source_evidence(self):
        self.r["sources"].append(copy.deepcopy(self.r["sources"][0]))
        self.bad()
    def test_unapproved_host(self):
        self.r["sources"][0]["requested_url"] = "https://example.com/private"
        self.bad()
    def test_changed_metadata_locator(self):
        self.r["sources"][0]["requested_url"] = m.METADATA["europe_pmc"].replace(m.PMID, "38447753")
        self.bad()
    def test_http_scheme_refused(self):
        self.r["sources"][0]["requested_url"] = self.r["sources"][0]["requested_url"].replace("https", "http")
        self.bad()
    def test_userinfo_refused(self):
        self.r["sources"][0]["requested_url"] = "https://user@www.ebi.ac.uk/fake"
        self.bad()
    def test_robots_refusal_cannot_be_acquired(self):
        self.r["sources"][0]["robots"]["decision"] = "refuse"
        self.bad()
    def test_guessed_fulltext_id_refused(self):
        s = copy.deepcopy(self.r["sources"][0])
        s.update(key="pmc_fulltext", requested_url="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC999999/fullTextXML")
        self.r["sources"].append(s)
        self.bad()
    def test_guessed_publisher_locator_refused(self):
        s = copy.deepcopy(self.r["sources"][1])
        s.update(key="publisher_landing", requested_url="https://www.sciencedirect.com/science/article/pii/GUESSED")
        self.r["sources"].append(s)
        self.bad()
    def test_unrecognized_source_key_refused(self):
        s = copy.deepcopy(self.r["sources"][0])
        s["key"] = "secondary_blog"
        self.r["sources"].append(s)
        self.bad()
    def test_invalid_status_cannot_silently_drop_source(self):
        self.r["sources"][0]["status"] = "ok"
        self.bad()
    def test_unicode_byte_count_not_character_count(self):
        self.r["sources"][1] = source("crossref", {"message": {"DOI": m.DOI, "title": ["évidence"]}})
        self.r["metadata_projection"] = m.metadata_fields(self.r["sources"])
        m.validate(self.r)
        self.r["sources"][1]["bytes"] = len(self.r["sources"][1]["raw_utf8"])
        self.bad()
    def test_changed_robots_bytes_refused(self):
        self.r["sources"][0]["robots"] = {"url": "https://www.ebi.ac.uk/robots.txt", "decision": "allow", "http_status": 200, "raw_utf8": "User-agent: *\nDisallow: /private",
              "bytes": 1, "sha256": "a" * 64}
        self.bad()
    def test_acquired_http_error_refused(self):
        self.r["sources"][0]["http_status"] = 403
        self.bad()
    def test_robots_policy_decision_flip_refused(self):
        raw = "User-agent: *\nDisallow: /"
        self.r["sources"][0]["robots"] = {"url": "https://www.ebi.ac.uk/robots.txt", "decision": "allow",
              "http_status": 200, "raw_utf8": raw, "bytes": len(raw.encode()), "sha256": m.sha(raw.encode())}
        self.bad()
    def test_valid_200_robots_policy_replayed(self):
        raw = "User-agent: *\nDisallow: /private"
        self.r["sources"][0]["robots"] = {"url": "https://www.ebi.ac.uk/robots.txt", "decision": "allow",
              "http_status": 200, "raw_utf8": raw, "bytes": len(raw.encode()), "sha256": m.sha(raw.encode())}
        m.validate(self.r)
    def test_robots_receipt_wrong_origin_refused(self):
        self.r["sources"][0]["robots"]["url"] = "https://api.crossref.org/robots.txt"
        self.bad()
    def test_robots_403_is_not_missing_policy(self):
        self.r["sources"][0]["robots"]["http_status"] = 403
        self.bad()
    def test_deadline_not_swallowed_by_robots(self):
        with patch.object(m, "request", side_effect=m.CycleDeadline("synthetic timeout")):
            with self.assertRaises(m.CycleDeadline):
                m.robots(m.METADATA["europe_pmc"])
    def test_deadline_not_swallowed_by_source_handler(self):
        allowed = {"url": "https://www.ebi.ac.uk/robots.txt", "decision": "allow_missing_robots", "http_status": 404}
        with patch.object(m, "robots", return_value=allowed):
            with patch.object(m, "request", side_effect=m.CycleDeadline("synthetic timeout")):
                with self.assertRaises(m.CycleDeadline):
                    m.acquire_source("europe_pmc", m.METADATA["europe_pmc"])
    def test_scope_escalation_refused(self):
        self.r["scope"] = "independent clinical validation"
        self.bad()

if __name__ == "__main__":
    unittest.main()
