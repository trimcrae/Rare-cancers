#include <zlib.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
struct Hit {string transcript,gene,window; size_t start;};
struct Best {int value; uint64_t count=0; set<string> genes; vector<Hit> witnesses; explicit Best(int v):value(v){} };
struct Result {Best gap{0},hamming{4};};
struct Design {string id,target; uint32_t code; array<Result,2> result;};
int base(char c){switch(c){case 'A':return 0;case 'C':return 1;case 'G':return 2;case 'T':case 'U':return 3;default:return -1;}}
vector<string> split(const string&s,char sep){vector<string>v;string p;istringstream z(s);while(getline(z,p,sep))v.push_back(p);return v;}
uint32_t encode(const string&s){uint32_t x=0;for(char c:s){int b=base(c);if(b<0)throw runtime_error("non-ACGT query");x=(x<<2)|b;}return x;}
int gap_length(uint32_t a,uint32_t b){int left=5,right=11;uint32_t x=a^b;while(left>0&&((x>>(2*(16-left)))&3)==0)--left;while(right<16&&((x>>(2*(15-right)))&3)==0)++right;return right-left;}
using Neighbors=unordered_map<uint32_t,vector<pair<uint16_t,uint8_t>>>;
void neighbors(Neighbors&m,uint32_t c,int from,int distance,int radius,uint16_t i){m[c].push_back({i,uint8_t(distance)});if(distance==radius)return;for(int p=from;p<16;++p){int shift=2*(15-p);uint32_t old=(c>>shift)&3;for(uint32_t b=0;b<4;++b)if(b!=old)neighbors(m,(c&~(uint32_t(3)<<shift))|(b<<shift),p+1,distance+1,radius,i);}}
void add(Best&b,int value,bool maximum,const string&tx,const string&gene,const string&seq,size_t start){bool better=maximum?value>b.value:value<b.value;if(better){b.value=value;b.count=0;b.genes.clear();b.witnesses.clear();}if(value==b.value){++b.count;b.genes.insert(gene);if(b.witnesses.size()<20)b.witnesses.push_back({tx,gene,seq.substr(start,16),start});}}
int main(int argc,char**argv){try{
 if(argc!=6)throw runtime_error("usage: scan queries.tsv input.fa[.gz] archived|gencode radius output-prefix");
 const string kind=argv[3];if(kind!="archived"&&kind!="gencode")throw runtime_error("invalid corpus kind");int radius=stoi(argv[4]);if(radius<0||radius>3)throw runtime_error("radius outside0..3");
 vector<Design>d;array<vector<uint16_t>,4096>seeds;Neighbors near;near.reserve(2000000);ifstream q(argv[1]);if(!q)throw runtime_error("cannot open queries");string line;set<string>ids;
 while(getline(q,line)){if(line.empty())continue;auto f=split(line,'\t');if(f.size()!=2||f[1].size()!=16||!ids.insert(f[0]).second)throw runtime_error("invalid/duplicate query");Design x;x.id=f[0];x.target=f[1];x.code=encode(x.target);for(auto&r:x.result)r.hamming.value=radius+1;d.push_back(x);}
 if(d.empty()||d.size()>1000)throw runtime_error("invalid query count");for(uint16_t i=0;i<d.size();++i){seeds[(d[i].code>>10)&4095].push_back(i);neighbors(near,d[i].code,0,0,radius,i);}
 set<string>parent={"EWSR1","TAF15","TCF12","FUS","TFG","NR4A3","PGR"},seen;uint64_t records=0,bases=0,windows=0,ambiguous=0;array<uint64_t,2>records_by{},windows_by{};string header,seq;
 auto process=[&](){if(header.empty())return;string tx,gene;int stratum=0;if(kind=="gencode"){auto h=split(header,'|');if(h.size()<8)throw runtime_error("GENCODE header field count");tx=h[0];gene=h[5];if(stoull(h[6])!=seq.size())throw runtime_error("GENCODE header length mismatch");stratum=parent.count(gene)?0:1;}else{tx=header;gene=header.substr(0,header.find(':'));if(!parent.count(gene))throw runtime_error("unexpected archived gene");}
 if(!seen.insert(tx).second)throw runtime_error("duplicate transcript record identifier");++records;++records_by[stratum];bases+=seq.size();uint32_t code=0;int valid=0;for(size_t p=0;p<seq.size();++p){int b=base(seq[p]);if(b<0){valid=0;code=0;}else{code=(code<<2)|uint32_t(b);valid=min(16,valid+1);}if(p<15)continue;if(valid<16){++ambiguous;continue;}++windows;++windows_by[stratum];size_t start=p-15;
 for(uint16_t i:seeds[(code>>10)&4095]){int value=gap_length(d[i].code,code);add(d[i].result[stratum].gap,value,true,tx,gene,seq,start);}
 auto n=near.find(code);if(n!=near.end())for(auto [i,distance]:n->second)add(d[i].result[stratum].hamming,distance,false,tx,gene,seq,start);
 }};
 gzFile in=gzopen(argv[2],"rb");if(!in)throw runtime_error("cannot open FASTA");array<char,65536>buf{};string pending;while(gzgets(in,buf.data(),buf.size())){pending+=buf.data();if(pending.empty()||pending.back()!='\n')continue;while(!pending.empty()&&(pending.back()=='\n'||pending.back()=='\r'))pending.pop_back();if(!pending.empty()&&pending[0]=='>'){process();header=pending.substr(1);seq.clear();}else{for(char c:pending)if(!isspace(static_cast<unsigned char>(c)))seq+=(toupper(static_cast<unsigned char>(c))=='U'?'T':toupper(static_cast<unsigned char>(c)));}pending.clear();}
 if(!pending.empty()){while(!pending.empty()&&pending.back()=='\r')pending.pop_back();if(pending[0]=='>'){process();header=pending.substr(1);seq.clear();}else for(char c:pending)if(!isspace(static_cast<unsigned char>(c)))seq+=(toupper(static_cast<unsigned char>(c))=='U'?'T':toupper(static_cast<unsigned char>(c)));}int error;const char*msg=gzerror(in,&error);string detail=msg?msg:"";if(error!=Z_OK&&error!=Z_STREAM_END)throw runtime_error("gzip read error:"+detail);gzclose(in);process();if(records==0)throw runtime_error("empty FASTA");
 ofstream summary(string(argv[5])+"-summary.tsv"),witness(string(argv[5])+"-witnesses.tsv"),meta(string(argv[5])+"-meta.tsv");if(!summary||!witness||!meta)throw runtime_error("cannot write output");summary<<"design_id\tstratum\tmetric\tvalue\texact\toccurrences\tgenes\n";witness<<"design_id\tstratum\tmetric\tvalue\ttranscript\tgene\tstart_0based\twindow_5to3\n";
 for(auto&x:d)for(int s=0;s<(kind=="gencode"?2:1);++s){string name=kind=="archived"?"archived_parent":s==0?"gencode_parent":"gencode_other";for(int m=0;m<2;++m){auto&v=m?x.result[s].hamming:x.result[s].gap;summary<<x.id<<'\t'<<name<<'\t'<<(m?"hamming":"gap")<<'\t'<<v.value<<'\t'<<(!m||v.count>0)<<'\t'<<v.count<<'\t';bool first=true;for(auto&g:v.genes){if(!first)summary<<';';summary<<g;first=false;}summary<<'\n';for(auto&h:v.witnesses)witness<<x.id<<'\t'<<name<<'\t'<<(m?"hamming":"gap")<<'\t'<<v.value<<'\t'<<h.transcript<<'\t'<<h.gene<<'\t'<<h.start<<'\t'<<h.window<<'\n';}}
 meta<<"records\tbases\tunambiguous_windows\tambiguous_windows\tparent_records\tother_records\tparent_windows\tother_windows\tquery_count\tradius\n"<<records<<'\t'<<bases<<'\t'<<windows<<'\t'<<ambiguous<<'\t'<<records_by[0]<<'\t'<<records_by[1]<<'\t'<<windows_by[0]<<'\t'<<windows_by[1]<<'\t'<<d.size()<<'\t'<<radius<<'\n';cerr<<"records="<<records<<" windows="<<windows<<" ambiguous="<<ambiguous<<" queries="<<d.size()<<"\n";
 summary.flush();witness.flush();meta.flush();if(!summary||!witness||!meta)throw runtime_error("output write/flush failed");
 return 0;
 }catch(const exception&e){cerr<<"ERROR: "<<e.what()<<'\n';return 1;}}
