// Certificate challenges, not the original scanner: literal strings and Aho-Corasick.
// All coordinates are target-sense 5'->3', core [5,11), full window length 16.
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
using namespace std;
void need(bool b,const string& s){if(!b)throw runtime_error(s);}
vector<string> split(const string&s,char c){vector<string>v;size_t p=0;
 for(;;){size_t e=s.find(c,p);v.push_back(s.substr(p,e==string::npos?e:e-p));if(e==string::npos)return v;p=e+1;}}
int base(char c){auto p=string("ACGT").find(c);return p==string::npos?-1:int(p);}
struct Q {string id,target;int h,g;int best=3;bool attain=false,beyond=false;
 string hw="-",gw="-",bw="-";};
struct Hit {int q,metric,value,left,length;};
struct Node {array<int,4> next{{-1,-1,-1,-1}};int fail=0;vector<int> out;};
struct AC {
 vector<Node> n{Node{}};vector<Hit> hits;
 void add(const string&s,Hit hit){int v=0;for(char c:s){int b=base(c);need(b>=0,"pattern alphabet");
   int w=n[v].next[b];if(w<0){w=int(n.size());n[v].next[b]=w;n.emplace_back();}v=w;}
   n[v].out.push_back(int(hits.size()));hits.push_back(hit);}
 void build(){queue<int>q;for(int b=0;b<4;++b){int w=n[0].next[b];if(w<0)n[0].next[b]=0;else q.push(w);}
  while(!q.empty()){int v=q.front();q.pop();for(int b=0;b<4;++b){int w=n[v].next[b];
   if(w<0){n[v].next[b]=n[n[v].fail].next[b];continue;}
   n[w].fail=n[n[v].fail].next[b];auto &out=n[n[w].fail].out;n[w].out.insert(n[w].out.end(),out.begin(),out.end());q.push(w);}}}
};
void neighborhood(AC&a,string&s,const string&original,int qi,int radius,int at=0,int distance=0){
 a.add(s,{qi,0,distance,0,16});if(distance==radius)return;
 for(int p=at;p<16;++p)for(char c:string("ACGT"))if(c!=original[p]){
 s[p]=c;neighborhood(a,s,original,qi,radius,p+1,distance+1);s[p]=original[p];}}
void gap_patterns(AC&a,const Q&q,int qi,int length,int metric){
 if(length>16)return;
 for(int l=0;l<=5;++l){int r=l+length;if(r>=11&&r<=16)a.add(q.target.substr(l,length),{qi,metric,length,l,length});}}
int main(int argc,char**argv){try{
 need(argc==5,"usage: extrema queries.tsv fasta[.gz] archived|gencode out-prefix");
 string kind=argv[3];need(kind=="archived"||kind=="gencode","corpus kind");
 ifstream input(argv[1]);need(bool(input),"query open");vector<Q>qs;set<string>ids;string line;
 while(getline(input,line)){if(!line.empty()&&line.back()=='\r')line.pop_back();auto f=split(line,'\t');
  need(f.size()==4,"query ID,target,union_hamming,union_gap required");
  Q q;q.id=f[0];q.target=f[1];q.h=stoi(f[2]);q.g=stoi(f[3]);
  need(!q.id.empty()&&ids.insert(q.id).second&&q.target.size()==16,"query ID/length");
  need(all_of(q.target.begin(),q.target.end(),[](char c){return base(c)>=0;}),"query alphabet");
  need(q.h>=0&&q.h<=2,"only exact union Hamming 0..2 supported");
  need(q.g==0||(q.g>=6&&q.g<=16),"gap must be zero or 6..16");qs.push_back(q);}
 need(!input.bad()&&!qs.empty()&&qs.size()<=1000,"query read/count");
 AC ac;for(int i=0;i<int(qs.size());++i){string s=qs[i].target;neighborhood(ac,s,qs[i].target,i,qs[i].h);
  if(qs[i].g)gap_patterns(ac,qs[i],i,qs[i].g,1);
  gap_patterns(ac,qs[i],i,max(6,qs[i].g+1),2);}ac.build();
 set<string>parents={"EWSR1","TAF15","TCF12","FUS","TFG","NR4A3","PGR"},seen;
 uint64_t records=0,bases=0,valid=0,ambiguous=0,parent_records=0,parent_windows=0;
 string header,seq;
 auto process=[&](){if(header.empty()){need(seq.empty(),"sequence before header");return;}
  string tx,gene;bool parent=true;
  if(kind=="gencode"){auto f=split(header,'|');need(f.size()>=8,"gencode header");tx=f[0];gene=f[5];
   need(stoull(f[6])==seq.size(),"header length mismatch");parent=parents.count(gene);}
  else {tx=header;gene=header.substr(0,header.find(':'));need(parents.count(gene),"archive gene");}
  need(!tx.empty()&&tx.find('\t')==string::npos&&seen.insert(tx).second,"duplicate/unsafe transcript");
  ++records;bases+=seq.size();parent_records+=parent;
  vector<uint32_t>bad(seq.size()+1);for(size_t p=0;p<seq.size();++p)bad[p+1]=bad[p]+(base(seq[p])<0);
  for(size_t p=0;p+16<=seq.size();++p){if(bad[p+16]==bad[p]){++valid;parent_windows+=parent;}else ++ambiguous;}
  int state=0;for(size_t p=0;p<seq.size();++p){int b=base(seq[p]);if(b<0){state=0;continue;}state=ac.n[state].next[b];
   for(int oi:ac.n[state].out){const auto&hit=ac.hits[oi];
    int64_t start=int64_t(p)+1-hit.length-hit.left;
    if(start<0||uint64_t(start)+16>seq.size())continue;
    size_t s=size_t(start);if(bad[s+16]!=bad[s])continue; // reject N anywhere in the aligned 16-mer
    auto&q=qs[hit.q];string witness=tx+":"+to_string(s)+":"+seq.substr(s,16);
    if(hit.metric==0){if(hit.value<q.best){q.best=hit.value;q.hw=witness;}}
    else if(hit.metric==1){if(!q.attain)q.gw=witness;q.attain=true;}
    else {if(!q.beyond)q.bw=witness;q.beyond=true;}
   }}
 };
 gzFile file=gzopen(argv[2],"rb");need(file,"FASTA open");array<char,65536>buf{};string pending;
 auto consume=[&](string l){while(!l.empty()&&(l.back()=='\r'||l.back()=='\n'))l.pop_back();
  if(l.empty())return;if(l[0]=='>'){process();header=l.substr(1);seq.clear();}
  else {need(!header.empty(),"sequence before header");for(unsigned char c:l)if(!isspace(c)){char b=char(toupper(c));seq+=(b=='U'?'T':b);}}};
 while(gzgets(file,buf.data(),int(buf.size()))){pending+=buf.data();if(!pending.empty()&&pending.back()=='\n'){consume(pending);pending.clear();}}
 if(!pending.empty())consume(pending);int err=0;const char*msg=gzerror(file,&err);string detail=msg?msg:"";
 int closed=gzclose(file);need((err==Z_OK||err==Z_STREAM_END)&&closed==Z_OK,"gzip read error:"+detail);process();need(records>0,"empty FASTA");
 ofstream out(string(argv[4])+"-certificates.tsv");need(bool(out),"output open");
 out<<"design_id\thamming_found\tgap_attained\tgap_exceeded\thamming_witness\tgap_witness\tcounterexample\n";
 for(auto&q:qs)out<<q.id<<'\t'<<q.best<<'\t'<<q.attain<<'\t'<<q.beyond<<'\t'<<q.hw<<'\t'<<q.gw<<'\t'<<q.bw<<'\n';
 out.flush();need(bool(out),"output write");
 ofstream meta(string(argv[4])+"-meta.tsv");need(bool(meta),"meta open");
 meta<<"records\tbases\tunambiguous_windows\tambiguous_windows\tparent_records\tother_records\tparent_windows\tother_windows\tquery_count\tpatterns\tstates\n"
 <<records<<'\t'<<bases<<'\t'<<valid<<'\t'<<ambiguous<<'\t'<<parent_records<<'\t'<<records-parent_records<<'\t'<<parent_windows<<'\t'<<valid-parent_windows<<'\t'<<qs.size()<<'\t'<<ac.hits.size()<<'\t'<<ac.n.size()<<'\n';
 meta.flush();need(bool(meta),"meta write");return 0;
 }catch(const exception&e){cerr<<e.what()<<'\n';return 1;}}

