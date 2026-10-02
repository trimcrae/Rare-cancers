// Independent exact 16-mer census: Aho-Corasick trie, no 2-bit rolling codes,
// gap seeds, query neighborhoods, or inputs from the original scanner results.
// Counts are transcript-record windows, not independent biological specimens.
#include <zlib.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr std::size_t K = 16;
struct Witness { std::string transcript, gene; std::uint64_t start; };
struct Census {
    std::uint64_t occurrences = 0;
    std::set<std::string> genes;
    std::vector<Witness> witnesses;
};
struct Query { std::string id, target; std::array<Census, 2> strata; };
struct Node {
    std::array<int, 4> next{{-1, -1, -1, -1}};
    int failure = 0;
    std::vector<std::size_t> outputs;
};
int symbol(unsigned char c) {
    switch (std::toupper(c)) {
    case 'A': return 0;
    case 'C': return 1;
    case 'G': return 2;
    case 'T': case 'U': return 3;
    default: return -1;
    }
}
void require(bool ok, const std::string& why) {
    if (!ok) throw std::runtime_error(why);
}
bool safe_field(const std::string& value) {
    return !value.empty() && value.find_first_of("\t\r\n") == std::string::npos;
}
std::vector<std::string> fields(const std::string& text, char delimiter) {
    std::vector<std::string> result;
    std::size_t begin = 0;
    for (;;) {
        auto end = text.find(delimiter, begin);
        result.push_back(text.substr(begin, end == std::string::npos ? end : end - begin));
        if (end == std::string::npos) return result;
        begin = end + 1;
    }
}
std::vector<Query> read_queries(const char* path) {
    std::ifstream file(path);
    require(bool(file), "Cannot open queries TSV");
    std::vector<Query> result;
    std::set<std::string> identifiers;
    std::string line;
    while (std::getline(file, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) continue;
        auto f = fields(line, '\t');
        require(f.size() == 2 && safe_field(f[0]) && f[1].size() == K,
                "Query must be ID<TAB>16-base target, without header");
        require(identifiers.insert(f[0]).second, "Duplicate query ID: " + f[0]);
        std::string normalized;
        for (unsigned char c : f[1]) {
            int s = symbol(c);
            require(s >= 0, "Ambiguous query target: " + f[0]);
            normalized += "ACGT"[s];
        }
        Query q; q.id = f[0]; q.target = normalized; result.push_back(q);
    }
    require(!file.bad(), "Query TSV read error");
    require(!result.empty() && result.size() <= 1000, "Unexpected query count");
    return result;
}
std::vector<Node> make_automaton(const std::vector<Query>& queries) {
    std::vector<Node> trie(1);
    for (std::size_t i = 0; i < queries.size(); ++i) {
        int state = 0;
        for (unsigned char c : queries[i].target) {
            int s = symbol(c);
            int child = trie[state].next[s];
            if (child == -1) {
                child = static_cast<int>(trie.size());
                trie[state].next[s] = child; // assign before vector reallocation
                trie.emplace_back();
            }
            state = child;
        }
        // Sequence-identical designs retain their separate IDs and counts.
        trie[state].outputs.push_back(i);
    }
    std::queue<int> pending;
    for (int s = 0; s < 4; ++s) {
        int child = trie[0].next[s];
        if (child == -1) trie[0].next[s] = 0;
        else { trie[child].failure = 0; pending.push(child); }
    }
    while (!pending.empty()) {
        int parent = pending.front(); pending.pop();
        for (int s = 0; s < 4; ++s) {
            int child = trie[parent].next[s];
            int fallback = trie[trie[parent].failure].next[s];
            if (child == -1) { trie[parent].next[s] = fallback; continue; }
            trie[child].failure = fallback;
            const auto inherited = trie[fallback].outputs;
            trie[child].outputs.insert(trie[child].outputs.end(), inherited.begin(), inherited.end());
            pending.push(child);
        }
    }
    return trie;
}
class Gzip {
public:
    gzFile handle;
    explicit Gzip(const char* path) : handle(gzopen(path, "rb")) {
        require(handle != nullptr, "Cannot open FASTA input");
    }
    ~Gzip() { if (handle) gzclose(handle); }
    void finish() {
        int status = gzclose(handle); handle = nullptr;
        require(status == Z_OK, "FASTA gzip close/integrity error");
    }
};
}

int main(int argc, char** argv) {
    try {
        require(argc == 4, "usage: verify_transcriptome queries.tsv gencode.fa[.gz] output-prefix");
        auto queries = read_queries(argv[1]);
        const auto trie = make_automaton(queries);
        const std::set<std::string> parents{"EWSR1", "TAF15", "TCF12", "FUS", "TFG", "NR4A3", "PGR"};
        std::set<std::string> seen;
        std::array<std::uint64_t, 2> records_by{}, windows_by{}, ambiguous_by{};
        std::uint64_t records = 0, bases = 0, windows = 0, ambiguous = 0;
        std::string transcript, gene;
        std::uint64_t length = 0, expected_length = 0;
        int stratum = 0, state = 0;
        std::size_t valid_run = 0;
        bool active = false;
        auto finish_record = [&]() {
            if (!active) return;
            require(length == expected_length, "GENCODE header length mismatch: " + transcript);
            ++records; ++records_by[stratum];
        };
        auto consume_line = [&](std::string line) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (line.empty()) return;
            if (line.front() == '>') {
                finish_record();
                auto h = fields(line.substr(1), '|');
                require(h.size() >= 8 && safe_field(h[0]) && safe_field(h[5]),
                        "Invalid GENCODE header fields");
                require(!h[6].empty() && h[6].find_first_not_of("0123456789") == std::string::npos,
                        "Invalid GENCODE header length");
                transcript = h[0]; gene = h[5]; expected_length = std::stoull(h[6]);
                require(seen.insert(transcript).second, "Duplicate transcript ID: " + transcript);
                stratum = parents.count(gene) ? 0 : 1;
                length = 0; state = 0; valid_run = 0; active = true;
                return;
            }
            for (unsigned char c : line) {
                if (std::isspace(c)) continue;
                require(active, "Sequence before first FASTA header");
                const int s = symbol(c);
                ++length; ++bases;
                if (s < 0) { state = 0; valid_run = 0; }
                else { state = trie[state].next[s]; valid_run = std::min(K, valid_run + 1); }
                if (length >= K) {
                    if (valid_run == K) { ++windows; ++windows_by[stratum]; }
                    else { ++ambiguous; ++ambiguous_by[stratum]; }
                }
                if (s < 0) continue;
                for (std::size_t qi : trie[state].outputs) {
                    require(length >= K && valid_run == K, "Automaton emitted an invalid window");
                    auto& out = queries[qi].strata[stratum];
                    ++out.occurrences; out.genes.insert(gene);
                    if (out.witnesses.size() < 20)
                        out.witnesses.push_back({transcript, gene, length - K});
                }
            }
        };
        Gzip input(argv[2]);
        std::array<char, 65536> buffer{};
        std::string line;
        for (;;) {
            int got = gzread(input.handle, buffer.data(), static_cast<unsigned int>(buffer.size()));
            if (got <= 0) {
                int status = Z_OK;
                const char* message = gzerror(input.handle, &status);
                require(got == 0 && (status == Z_OK || status == Z_STREAM_END) && gzeof(input.handle),
                        std::string("FASTA gzip read/integrity error: ") + (message ? message : "unknown"));
                break;
            }
            for (int p = 0; p < got; ++p) {
                char c = buffer[p];
                if (c == '\n') { consume_line(line); line.clear(); }
                else line.push_back(c);
            }
        }
        if (!line.empty()) consume_line(line);
        input.finish(); finish_record();
        require(records > 0, "No FASTA records");
        const std::string prefix = argv[3];
        std::ofstream summary(prefix + "-summary.tsv"), witnesses(prefix + "-witnesses.tsv"), meta(prefix + "-meta.tsv");
        require(bool(summary) && bool(witnesses) && bool(meta), "Cannot open census outputs");
        summary << "design_id\tstratum\toccurrences\n";
        witnesses << "design_id\tstratum\ttranscript\tgene\tstart_0based\twindow_5to3\n";
        for (const auto& q : queries) {
            for (int s = 0; s < 2; ++s) {
                const auto& out = q.strata[s];
                const char* label = s == 0 ? "gencode_parent" : "gencode_other";
                summary << q.id << '\t' << label << '\t' << out.occurrences << '\n';
                for (const auto& hit : out.witnesses)
                    witnesses << q.id << '\t' << label << '\t' << hit.transcript << '\t' << hit.gene
                              << '\t' << hit.start << '\t' << q.target << '\n';
            }
        }
        meta << "records\tbases\tunambiguous_windows\tambiguous_windows\tparent_records\tother_records\tparent_windows\tother_windows\tquery_count\n"
             << records << '\t' << bases << '\t' << windows << '\t' << ambiguous << '\t'
             << records_by[0] << '\t' << records_by[1] << '\t' << windows_by[0] << '\t' << windows_by[1] << '\t'
             << queries.size() << '\n';
        summary.flush(); witnesses.flush(); meta.flush();
        require(bool(summary) && bool(witnesses) && bool(meta), "Census output write/flush failure");
        summary.close(); witnesses.close(); meta.close();
        require(bool(summary) && bool(witnesses) && bool(meta), "Census output close failure");
        std::cerr << "Aho-Corasick exact census complete: records=" << records << " windows=" << windows
                  << " queries=" << queries.size() << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
