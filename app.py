import streamlit as st
import json, pandas as pd, time, urllib.parse
from discovery.youtube import YouTubeDiscovery
from discovery.instagram import InstagramDiscovery
from intelligence.analyzer import ContentAnalyzer
from intelligence.scorer import BrandFitScorer
from intelligence.outreach import OutreachGenerator
from utils.logger import (
    print_banner, print_discovery_results, print_analysis_result,
    print_outreach_preview, print_summary_table, print_save_confirmation, console
)
from utils.exporter import Exporter
st.set_page_config(page_title="OutreachOS", layout="wide", initial_sidebar_state="expanded")

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#f3fafd;color:#1a3a4a;}
.main .block-container{padding:2rem 2rem;max-width:100%;}
section[data-testid="stSidebar"]{background:#e8f5fb;border-right:1px solid #c9e9f6;}
.card{background:#ffffff;border-radius:12px;padding:20px;border:1px solid #c9e9f6;box-shadow:0 4px 20px rgba(69,179,224,.08);margin-bottom:16px;}
.card-accent{border-left:3px solid #45b3e0;}
.metric-card{background:#ffffff;border-radius:12px;padding:20px;border:1px solid #c9e9f6;text-align:center;box-shadow:0 2px 12px rgba(69,179,224,.08);}
.mn{font-size:2.2rem;font-weight:700;color:#45b3e0;line-height:1;}
.mn-g{font-size:2.2rem;font-weight:700;color:#27ae60;line-height:1;}
.mn-y{font-size:2.2rem;font-weight:700;color:#e67e22;line-height:1;}
.ml{font-size:.8rem;color:#5a8fa0;margin-top:6px;}
.sh{font-size:1rem;font-weight:600;color:#1a3a4a;padding-bottom:8px;border-bottom:1px solid #c9e9f6;margin-bottom:16px;}
.tag{display:inline-block;background:#e0f4fc;color:#2980b9;border-radius:20px;padding:3px 10px;font-size:.72rem;margin:2px;}
.by{background:#fde8e8;color:#c0392b;border-radius:4px;padding:2px 8px;font-size:.72rem;font-weight:600;}
.bi{background:#ede8fd;color:#7d3c98;border-radius:4px;padding:2px 8px;font-size:.72rem;font-weight:600;}
.b-rd{background:#e8f8f0;color:#1e8449;border-radius:4px;padding:2px 10px;font-size:.75rem;font-weight:600;}
.b-rv{background:#fef5e4;color:#b7770d;border-radius:4px;padding:2px 10px;font-size:.75rem;font-weight:600;}
.b-fl{background:#fde8e8;color:#c0392b;border-radius:4px;padding:2px 10px;font-size:.75rem;font-weight:600;}
.sp-done{background:#45b3e0;color:#fff;border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600;display:inline-block;margin:4px;}
.sp-active{background:#d6f0fa;color:#1a7aab;border:1px solid #45b3e0;border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600;display:inline-block;margin:4px;}
.sp-pend{background:#f3fafd;color:#7aacbd;border:1px solid #c9e9f6;border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600;display:inline-block;margin:4px;}
.bar-w{background:#c9e9f6;border-radius:20px;height:8px;width:100%;overflow:hidden;}
.bar-g{height:8px;border-radius:20px;background:#27ae60;}
.bar-y{height:8px;border-radius:20px;background:#e67e22;}
.bar-r{height:8px;border-radius:20px;background:#e74c3c;}
.hero-t{font-size:3rem;font-weight:700;text-align:center;line-height:1.2;color:#1a3a4a;}
.hero-s{font-size:1.1rem;color:#5a8fa0;text-align:center;margin:12px 0 32px 0;}
.ob{background:#f3fafd;border:1px solid #c9e9f6;border-radius:8px;padding:16px;font-size:.85rem;line-height:1.6;white-space:pre-wrap;color:#1a3a4a;}
.wb{background:#fef5e4;border:1px solid #f0c040;border-radius:8px;padding:10px 14px;font-size:.8rem;color:#7d5a00;margin:8px 0;}
.tg{color:#1e8449;font-size:.8rem;font-weight:600;}
.tr{color:#c0392b;font-size:.8rem;font-weight:600;}
.tb{color:#2980b9;font-size:.8rem;font-weight:600;}
.foot{text-align:center;color:#7aacbd;font-size:.75rem;padding:24px 0 8px 0;border-top:1px solid #c9e9f6;margin-top:40px;}
</style>"""

MOCK = [
    {"creator_handle":"@skincarewithpriya","platform":"YouTube","followers":24300,"engagement_rate":4.2,"avg_views":18000,"posting_frequency":"3-4x/week","niche":"Budget Skincare","content_themes":["skincare routines","product reviews","affordable beauty"],"recent_signals":["Top 5 Budget Moisturizers","#skincareindia","dermat tips"],"brand_fit_score":87,"fit_explanation":"High fit: covers budget skincare matching product, targets women 18-24, posts regularly.","engagement_quality":"Genuine","engagement_reason":"Consistent comment-to-like ratio, organic growth.","competitor_flag":False,"competitor_detail":None,"growth_trend":"Growing","collaboration_recommended":"Product Trial","email_subject":"Collaboration Opportunity — [Brand] x @skincarewithpriya","email_body":"Hi Priya,\n\nI've been following your skincare content and love how you break down affordable routines. Your recent video on budget moisturizers was especially insightful.\n\nAt [Brand], we create science-backed skincare products for the Indian climate. We believe your audience would genuinely benefit from trying our range, and your authentic review style is a perfect fit.\n\nWould you be open to a product trial collaboration this month?\n\nWarm regards,\n[Your Name]\n[Brand] Partnerships Team","dm_message":"Hi Priya, love your budget skincare content. We are from [Brand] and think your audience would love our products. Open to a trial collab?","outreach_signals_used":"video: Top 5 Budget Moisturizers, hashtag: skincareindia","profile_link":"https://youtube.com/@skincarewithpriya","contact_email":"priya@email.com"},
    {"creator_handle":"@financewithrohit","platform":"YouTube","followers":67200,"engagement_rate":3.8,"avg_views":42000,"posting_frequency":"2x/week","niche":"Personal Finance","content_themes":["SIP investing","budgeting tips","credit card hacks"],"recent_signals":["Best SIP Plans 2024","#personalfinanceindia","credit score tips"],"brand_fit_score":91,"fit_explanation":"Very high fit: finance-focused audience aligns with fintech product, strong 22-35 age group.","engagement_quality":"Genuine","engagement_reason":"High share-to-view ratio indicating strong content resonance.","competitor_flag":True,"competitor_detail":"Promoted GrowIndia app 3 weeks ago.","growth_trend":"Growing","collaboration_recommended":"Affiliate Program","email_subject":"Affiliate Partnership — [Brand] x @financewithrohit","email_body":"Hi Rohit,\n\nYour breakdown of SIP investment strategies has been outstanding. The way you simplify complex financial concepts for everyday Indians is exactly the communication style we value.\n\nAt [Brand], we offer a fintech platform helping users manage SIPs and track credit scores. Given your audience's deep interest in personal finance, an affiliate partnership would create real value on both sides.\n\nWould you be interested in exploring this?\n\nBest,\n[Your Name]","dm_message":"Hi Rohit, your SIP content is excellent. We are from [Brand] and would love to discuss an affiliate partnership. Interested?","outreach_signals_used":"video: Best SIP Plans 2024, hashtag: personalfinanceindia","profile_link":"https://youtube.com/@financewithrohit","contact_email":"rohit@gmail.com"},
    {"creator_handle":"@glowupwithmeera","platform":"Instagram","followers":38900,"engagement_rate":5.1,"avg_views":22000,"posting_frequency":"5x/week","niche":"Makeup Tutorials","content_themes":["everyday makeup","drugstore finds","skincare prep"],"recent_signals":["Drugstore Foundation Routine","#makeupindia","no-filter skin"],"brand_fit_score":78,"fit_explanation":"Good fit: makeup audience overlaps with skincare users, high engagement rate indicates trust.","engagement_quality":"Genuine","engagement_reason":"Authentic comments with specific product questions, low bot activity.","competitor_flag":False,"competitor_detail":None,"growth_trend":"Stable","collaboration_recommended":"Barter Collaboration","email_subject":"Barter Collab Proposal — [Brand] x @glowupwithmeera","email_body":"Hi Meera,\n\nYour everyday makeup tutorials are consistently among the most helpful on the platform. The way you incorporate skincare prep shows real expertise.\n\nAt [Brand], we specialize in skincare products that create the perfect base for makeup. We would love to send you our starter kit for an honest review and integration into one of your upcoming tutorials.\n\nLet us know if this interests you.\n\nWarm regards,\n[Your Name]","dm_message":"Hi Meera, love your makeup tutorials. We are from [Brand] and would love to send our skincare range for an honest review. Open to it?","outreach_signals_used":"post: Drugstore Foundation Routine, hashtag: makeupindia","profile_link":"https://instagram.com/glowupwithmeera","contact_email":None},
    {"creator_handle":"@class10endgame","platform":"YouTube","followers":7350,"engagement_rate":6.2,"avg_views":9800,"posting_frequency":"Daily","niche":"CBSE Education","content_themes":["Class 10 board prep","one-shot revisions","exam strategies"],"recent_signals":["Class 10 Math One-Shot","#cbse2025","board exam tips"],"brand_fit_score":95,"fit_explanation":"Excellent fit: creator targets Class 10 students exclusively, aligns directly with Olympiad preparation.","engagement_quality":"Genuine","engagement_reason":"High comment volume with study-related questions, strong community.","competitor_flag":False,"competitor_detail":None,"growth_trend":"Growing","collaboration_recommended":"Paid Sponsorship","email_subject":"Partnership Opportunity — SPARK Olympiads x @class10endgame","email_body":"Hi,\n\nYour Class 10 one-shot revision series has been exceptional. The clarity with which you cover the full syllabus shows a deep understanding of what board students need.\n\nAt SPARK Olympiads, we run India's leading school-level competitive assessment platform. Your audience of high-intent Class 10 students is an exact match for our Olympiad programs. We would love to explore a sponsored integration.\n\nWould you be open to a quick call this week?\n\nBest regards,\nSPARK Olympiads Team","dm_message":"Hi, your Class 10 revision content is excellent. We are from SPARK Olympiads and would love to collaborate on an Olympiad prep session for your students.","outreach_signals_used":"video: Class 10 Math One-Shot, hashtag: cbse2025","profile_link":"https://youtube.com/@class10endgame","contact_email":None},
    {"creator_handle":"@wellnesswithsara","platform":"Instagram","followers":51000,"engagement_rate":2.1,"avg_views":15000,"posting_frequency":"2x/week","niche":"Health & Wellness","content_themes":["yoga routines","clean eating","mental wellness"],"recent_signals":["Morning Yoga Routine","#wellnessindia","mindful eating"],"brand_fit_score":62,"fit_explanation":"Moderate fit: wellness audience may overlap but direct product alignment is indirect.","engagement_quality":"Suspicious","engagement_reason":"Below-average comment ratio, rapid follower growth spikes detected.","competitor_flag":False,"competitor_detail":None,"growth_trend":"Stable","collaboration_recommended":"UGC Partnership","email_subject":"UGC Collaboration — [Brand] x @wellnesswithsara","email_body":"Hi Sara,\n\nYour mindful approach to wellness content stands out. The morning yoga routine you posted recently was practical and calming.\n\nAt [Brand], we are building content around holistic wellness and looking for authentic creators for user-generated content. We believe a UGC collaboration could be a great mutual fit.\n\nWould you be open to learning more?\n\nBest,\n[Your Name]","dm_message":"Hi Sara, your wellness content is authentic. We are from [Brand] and would love to explore a UGC collaboration. Interested?","outreach_signals_used":"post: Morning Yoga Routine, hashtag: wellnessindia","profile_link":"https://instagram.com/wellnesswithsara","contact_email":"sara@gmail.com"},
    {"creator_handle":"@techwitharjun","platform":"YouTube","followers":89400,"engagement_rate":3.5,"avg_views":55000,"posting_frequency":"3x/week","niche":"SaaS & Tech Reviews","content_themes":["app reviews","productivity tools","startup tools"],"recent_signals":["Best Productivity Apps 2024","#saastools","no-code tools India"],"brand_fit_score":73,"fit_explanation":"Good fit: tech-savvy audience aligns with SaaS product, strong viewer intent for tool discovery.","engagement_quality":"Genuine","engagement_reason":"Strong watch time metrics inferred from high view-to-sub ratio.","competitor_flag":True,"competitor_detail":"Reviewed a competing SaaS platform 2 months ago.","growth_trend":"Growing","collaboration_recommended":"Paid Sponsorship","email_subject":"Sponsorship Proposal — [Brand] x @techwitharjun","email_body":"Hi Arjun,\n\nYour reviews of productivity and SaaS tools are among the most trusted in the Indian tech creator space. The way you evaluate tools from a real-user perspective adds genuine credibility.\n\nAt [Brand], we have built a platform we believe your audience would find immediately useful. We would love to explore a sponsored segment in your upcoming content calendar.\n\nWould you be interested in a product walkthrough call?\n\nBest,\n[Your Name]","dm_message":"Hi Arjun, your SaaS reviews are great. We are from [Brand] and think our platform would resonate with your audience. Open to a sponsored review?","outreach_signals_used":"video: Best Productivity Apps 2024, hashtag: saastools","profile_link":"https://youtube.com/@techwitharjun","contact_email":"arjun@gmail.com"},
]


def ffmt(n):
    if n>=1000000: return f"{n/1000000:.1f}M"
    if n>=1000: return f"{n/1000:.1f}K"
    return str(n)

def bar(score):
    c = "bar-g" if score>=75 else ("bar-y" if score>=50 else "bar-r")
    return f"<div class='bar-w'><div class='{c}' style='width:{score}%'></div></div>"

def stepper(stage):
    stages=["Discovering Creators","Filtering & Validating","Analyzing Content","Scoring Brand Fit","Generating Outreach"]
    msgs=["Searching YouTube and Instagram...","Applying filters and validating creators...","Extracting content signals with AI...","Computing brand-fit scores...","Generating personalized outreach messages..."]
    h="<div style='margin-bottom:12px;padding:16px;background:#162236;border-radius:12px;border:1px solid #1E3A5F'>"
    for i,s in enumerate(stages):
        if i<stage: h+=f"<span class='sp-done'>{s}</span>"
        elif i==stage: h+=f"<span class='sp-active'>{s}</span>"
        else: h+=f"<span class='sp-pend'>{s}</span>"
    h+="</div>"
    st.markdown(h,unsafe_allow_html=True)
    if stage<len(msgs): st.caption(msgs[stage])

def sidebar():
    with st.sidebar:
        st.markdown("<div class='sh' style='font-size:1.4rem;border:none'>OutreachOS</div>",unsafe_allow_html=True)
        st.markdown("<div style='font-size:.8rem;color:#5a8fa0;margin-top:-12px;margin-bottom:12px'>Influencer Intelligence Platform</div>",unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#c9e9f6;margin:0 0 16px 0'>",unsafe_allow_html=True)
        st.markdown("<div class='sh'>Campaign Setup</div>",unsafe_allow_html=True)
        bn=st.text_input("Brand Name",placeholder="e.g. Mamaearth",key="brand_name")
        brief=st.text_area("Brand Brief",placeholder="Describe your brand, target audience, product category, and campaign goal...",key="brand_brief",height=90)
        ind=st.selectbox("Industry / Category",["Beauty & Skincare","Education & Learning","Finance & Fintech","Lifestyle & Wellness","D2C Products","SaaS & Tech","Food & Nutrition","Fashion & Apparel","Health & Fitness","Travel & Tourism"],key="industry")
        kw=st.text_input("Target Keywords",placeholder="e.g. skincare routine India",key="keywords")
        st.caption("Separate multiple keywords with commas")
        max_creators = st.slider("Number of Creators to Analyze", min_value=1, max_value=20, value=5, key="max_creators")
        st.markdown("<div class='sh' style='margin-top:16px'>Discovery Filters</div>",unsafe_allow_html=True)
        fr=st.slider("Follower Range",1000,500000,(5000,100000),step=1000,key="follower_range")
        st.caption(f"{ffmt(fr[0])} — {ffmt(fr[1])}")
        st.selectbox("Region",["India","Pan India","Metro Cities Only","Tier 2 Cities"],key="region")
        st.selectbox("Platforms",["YouTube Only","Instagram Only","Both Platforms"],key="platforms")
        st.selectbox("Content Activity",["Last 7 days","Last 30 days","Last 90 days"],key="activity")
        st.markdown("<div class='sh' style='margin-top:16px'>Outreach Settings</div>",unsafe_allow_html=True)
        tone=st.selectbox("Brand Tone",["Professional","Friendly","Casual","Formal"],key="tone")
        st.selectbox("Collaboration Type",["Paid Sponsorship","Affiliate Program","Barter Collaboration","UGC Partnership","Product Trial","Brand Ambassador"],key="collab_type")
        st.checkbox("Flag Fake Engagement",value=True,key="flag_fake")
        st.checkbox("Flag Competitor Mentions",value=True,key="flag_competitor")
        st.markdown("<br>",unsafe_allow_html=True)
        run=st.button("Run Discovery",type="primary",use_container_width=True,key="run_btn")
        clr=st.button("Clear Results",use_container_width=True,key="clear_btn")
        return run,clr,bn,ind,kw,tone,max_creators,brief,fr

def hero():
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown("<div class='hero-t'>Discover. Analyze. Outreach.</div>",unsafe_allow_html=True)
    st.markdown("<div class='hero-s'>Enter your brand details and keywords to discover micro-influencers and generate personalized outreach in seconds.</div>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    for col,(t,d) in zip([c1,c2,c3,c4],[("Real-Time Discovery","Live search across YouTube and Instagram"),("AI Content Analysis","Deep content signal extraction"),("Brand-Fit Scoring","Dynamic relevance matching"),("Personalized Outreach","Context-aware message generation")]):
        with col: st.markdown(f"<div class='card card-accent'><div style='font-size:.9rem;font-weight:600;margin-bottom:6px;color:#E8EDF5'>{t}</div><div style='font-size:.8rem;color:#8FA3C0'>{d}</div></div>",unsafe_allow_html=True)

def metrics(data):
    ae=sum(d["engagement_rate"] for d in data)/len(data)
    af=sum(d["brand_fit_score"] for d in data)/len(data)
    rd=sum(1 for d in data if d.get("outreach", {}).get("professional", {}).get("email", "") not in ["", "Error"])
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='mn'>{len(data)}</div><div class='ml'>Creators Found</div></div>",unsafe_allow_html=True)
    ec="mn-g" if ae>=3 else "mn-y"
    with c2: st.markdown(f"<div class='metric-card'><div class='{ec}'>{ae:.1f}%</div><div class='ml'>Avg. Engagement Rate</div></div>",unsafe_allow_html=True)
    fc="mn-g" if af>=75 else "mn-y"
    with c3: st.markdown(f"<div class='metric-card'><div class='{fc}'>{af:.0f}%</div><div class='ml'>Avg. Brand Fit Score</div></div>",unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'><div class='mn'>{rd}</div><div class='ml'>Outreach Ready</div></div>",unsafe_allow_html=True)

def tab_profiles(data, bn):
    st.markdown("<div class='sh'>Creator Profiles</div>",unsafe_allow_html=True)
    for d in data:
        bdg="by" if d["platform"]=="YouTube" else "bi"
        th=" ".join([f"<span class='tag'>{t}</span>" for t in d["content_themes"]])
        eq="tg" if d["engagement_quality"]=="Genuine" else "tr"
        tc={"Growing":"tg","Stable":"tb","Declining":"tr"}.get(d["growth_trend"],"tb")
        
        # Profile Picture Fallback
        handle_quoted = urllib.parse.quote(d["creator_handle"])
        pic = d.get("profile_pic")
        if not pic:
            pic = f"https://ui-avatars.com/api/?name={handle_quoted}&background=e8f5fb&color=45b3e0&size=150"
            
        # Outreach
        st.markdown(f"""<div class='card' style='display:flex; flex-direction:column; gap:16px; margin-bottom:0; border-bottom-left-radius:0; border-bottom-right-radius:0;'>
<div style='display:flex; gap: 20px; align-items:flex-start;'>
<div style='display:flex; flex-direction:column; align-items:center; width: 100px; flex-shrink: 0;'>
<img src='{pic}' style='width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #c9e9f6;margin-bottom:10px;'>
<span class='{bdg}'>{d["platform"]}</span>
</div>
<div style='flex: 1;'>
<div style='display:flex;align-items:center;margin-bottom:8px'>
<span style='font-size:1.2rem;font-weight:700;color:#1a3a4a;margin-right:12px;'>{d["creator_handle"]}</span>
{th}
</div>
<div style='display:flex;gap:12px;margin-bottom:12px'>
<div style='background:#e8f5fb;border-radius:8px;padding:8px 12px;flex:1;text-align:center'>
<div style='color:#45b3e0;font-weight:700'>{d["engagement_rate"]}%</div>
<div style='color:#5a8fa0;font-size:.72rem'>Engagement</div>
</div>
<div style='background:#e8f5fb;border-radius:8px;padding:8px 12px;flex:1;text-align:center'>
<div style='color:#45b3e0;font-weight:700'>{ffmt(d["avg_views"])}</div>
<div style='color:#5a8fa0;font-size:.72rem'>Avg. Views</div>
</div>
<div style='background:#e8f5fb;border-radius:8px;padding:8px 12px;flex:1;text-align:center'>
<div style='color:#45b3e0;font-weight:700'>{d["posting_frequency"]}</div>
<div style='color:#5a8fa0;font-size:.72rem'>Frequency</div>
</div>
<div style='background:#f3fafd;border: 1px solid #c9e9f6; border-radius:8px;padding:8px 12px;flex:1;text-align:center'>
<div style='color:#1a3a4a;font-weight:700'>{ffmt(d["followers"])}</div>
<div style='color:#5a8fa0;font-size:.72rem'>Followers</div>
</div>
</div>
<div style='display:flex;align-items:center;gap:12px;margin-bottom:6px'>
        <div style='flex:1;'>{bar(d["brand_fit_score"])}</div>
        <span style='font-weight:700;color:#1a3a4a;white-space:nowrap;'>{d["brand_fit_score"]}% Fit</span>
      </div>
      <div style='color:#5a8fa0;font-size:.78rem;margin-bottom:8px'>{d["fit_explanation"]}</div>
      <div style='display:flex; gap:16px; font-size:.78rem;'>
          <div class='{eq}'>{d["engagement_quality"]} Engagement</div>
          <div class='{tc}'>Trend: {d["growth_trend"]}</div>
      </div>
    </div>
  </div>
</div>
""",unsafe_allow_html=True)

        t_prof, t_friend, t_cas = st.tabs(["💼 Professional", "👋 Friendly", "☕ Casual"])
        tones = ["professional", "friendly", "casual"]
        tabs = [t_prof, t_friend, t_cas]
        outreach = d.get("outreach", {})
        
        for t, tone_key in zip(tabs, tones):
            with t:
                tone_data = outreach.get(tone_key, {})
                email_body = tone_data.get("email", "No email generated.")
                dm_body = tone_data.get("dm", "")
                
                subject = f"Collaboration Inquiry - {bn}"
                gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&tf=1&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(email_body)}"
                
                st.markdown(f"""
                <div style='background:#f3fafd;border:1px solid #c9e9f6;border-top:none;border-radius:0 0 8px 8px;padding:16px;'>
                     <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>
                        <span style='font-size:.9rem;font-weight:600;color:#1a3a4a;'>Generated {tone_key.title()} Pitch</span>
                        <a href='{gmail_url}' target='_blank' style='background:#ea4335;color:white;padding:6px 16px;border-radius:6px;text-decoration:none;font-size:.8rem;font-weight:600;box-shadow:0 2px 4px rgba(234,67,53,.2);'>✉ Send via Gmail</a>
                     </div>
                     <div style='display:flex; gap:16px;'>
                         <div style='flex:1;'>
                             <div style='font-size:.75rem; font-weight:600; color:#5a8fa0; margin-bottom:4px;'>EMAIL</div>
                             <div style='font-size:.8rem;color:#1a3a4a;white-space:pre-wrap;line-height:1.5;'>{email_body}</div>
                         </div>
                         <div style='width:1px; background:#c9e9f6;'></div>
                         <div style='flex:1;'>
                             <div style='font-size:.75rem; font-weight:600; color:#5a8fa0; margin-bottom:4px;'>INSTAGRAM DM</div>
                             <div style='font-size:.8rem;color:#1a3a4a;white-space:pre-wrap;line-height:1.5;'>{dm_body}</div>
                         </div>
                     </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

def tab_table(data):
    st.markdown("<div class='sh'>Comparison Table</div>",unsafe_allow_html=True)
    sc,fc,qc=st.columns(3)
    with sc: sort_by=st.selectbox("Sort by",["Brand Fit Score","Followers","Engagement Rate"],key="sort_by")
    with fc: plat_f=st.selectbox("Platform",["All","YouTube","Instagram"],key="plat_f")
    with qc: qual_f=st.selectbox("Quality",["All","Genuine Only"],key="qual_f")
    df=pd.DataFrame([{"Handle":d["creator_handle"],"Platform":d["platform"],"Followers":d["followers"],"Engagement %":d["engagement_rate"],"Fit Score":d["brand_fit_score"],"Niche":d["niche"],"Quality":d["engagement_quality"],"Collab":d["collaboration_recommended"]} for d in data])
    if plat_f!="All": df=df[df["Platform"]==plat_f]
    if qual_f=="Genuine Only": df=df[df["Quality"]=="Genuine"]
    sk={"Brand Fit Score":"Fit Score","Followers":"Followers","Engagement Rate":"Engagement %"}.get(sort_by,"Fit Score")
    df=df.sort_values(sk,ascending=False)
    st.dataframe(df,use_container_width=True,hide_index=True)
    
    # Add CSV Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Marketing Spreadsheet (CSV)",
        data=csv,
        file_name="outreachos_campaign_export.csv",
        mime="text/csv",
        use_container_width=True
    )

def tab_intel(data):
    st.markdown("<div class='sh'>Content Intelligence</div>",unsafe_allow_html=True)
    for d in data:
        th=" ".join([f"<span class='tag'>{t}</span>" for t in d["content_themes"]])
        sig="<br>".join([f"• {s}" for s in d["recent_signals"]])
        tc={"Growing":"tg","Stable":"tb","Declining":"tr"}.get(d["growth_trend"],"tb")
        st.markdown(f"""<div class='card'>
<div style='font-weight:600;font-size:1rem;margin-bottom:10px'>{d["creator_handle"]}</div>
<div style='margin-bottom:10px'><div style='color:#5a8fa0;font-size:.78rem;margin-bottom:4px'>Content Themes Detected</div>{th}</div>
<div style='margin-bottom:10px'><div style='color:#5a8fa0;font-size:.78rem;margin-bottom:4px'>Recent Content Signals</div><div style='font-size:.82rem;line-height:1.8'>{sig}</div></div>
<div style='margin-bottom:6px'><div style='color:#5a8fa0;font-size:.78rem;margin-bottom:2px'>Posting Pattern</div><div style='font-size:.82rem'>{d["posting_frequency"]}</div></div>
<div style='margin-bottom:6px'><div style='color:#5a8fa0;font-size:.78rem;margin-bottom:2px'>Niche</div><div style='font-size:.82rem'>{d["niche"]}</div></div>
<div><div style='color:#5a8fa0;font-size:.78rem;margin-bottom:2px'>Growth Trend</div><div class='{tc}'>{d["growth_trend"]}</div></div>
</div>""",unsafe_allow_html=True)

def tab_outreach(data):
    st.markdown("<div class='sh'>Outreach Manager</div>",unsafe_allow_html=True)
    rows=[]
    for d in data:
        has_email=d.get("email_body","") not in ["","Error"]
        flag=d.get("competitor_flag",False)
        eng=d.get("engagement_quality","")=="Suspicious"
        if flag or eng: status="Flagged"; sbdg="b-fl"
        elif has_email: status="Ready to Send"; sbdg="b-rd"
        else: status="Review Needed"; sbdg="b-rv"
        rows.append({"creator":d["creator_handle"],"platform":d["platform"],"has_email":has_email,"status":status,"sbdg":sbdg,"dm":d.get("dm_message","")})
    for r in rows:
        c1,c2,c3,c4,c5=st.columns([2,1,1,1,1])
        with c1: st.markdown(f"**{r['creator']}**")
        with c2: st.caption(r["platform"])
        with c3: st.caption("Yes" if r["has_email"] else "No")
        with c4: st.markdown(f"<span class='{r['sbdg']}'>{r['status']}</span>",unsafe_allow_html=True)
        with c5:
            if st.button("Send Email",key=f"send_{r['creator']}"):
                st.toast(f"Email queued for {r['creator']}",icon=None)
    st.markdown("<br>",unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        csv_data = []
        for d in data:
            csv_data.append({
                "Creator Handle": d.get("creator_handle"),
                "Platform": d.get("platform"),
                "Followers": d.get("followers"),
                "Engagement Rate (%)": d.get("engagement_rate"),
                "Avg Views": d.get("avg_views"),
                "Niche": d.get("niche"),
                "Fit Score": d.get("brand_fit_score"),
                "Fit Reasoning": d.get("fit_explanation"),
                "Contact Email": d.get("contact_email"),
                "Email Subject": d.get("email_subject"),
                "Generated Email": d.get("email_body"),
                "Generated DM": d.get("dm_message")
            })
        csv=pd.DataFrame(csv_data).to_csv(index=False)
        st.download_button("Export Full Campaign to CSV",data=csv,file_name="campaign_export.csv",mime="text/csv",use_container_width=True)
    with col2:
        jdata=json.dumps(data,indent=2)
        st.download_button("Export Creator Report as JSON",data=jdata,file_name="creator_report.json",mime="application/json",use_container_width=True)

def tab_strategy(data,brand_name,industry):
    st.markdown("<div class='sh'>Campaign Strategy</div>",unsafe_allow_html=True)
    bn=brand_name or "[Brand]"
    st.markdown(f"<div class='card'><div style='color:#8FA3C0;font-size:.85rem'>Based on <strong style='color:#E8EDF5'>{len(data)} creators</strong> discovered for <strong style='color:#6BA3F5'>{bn}</strong> in <strong style='color:#E8EDF5'>{industry}</strong>, here is your recommended campaign strategy.</div></div>",unsafe_allow_html=True)
    segs={}
    for d in data:
        s=d.get("segment_name", "Segment A: General Audience")
        segs.setdefault(s,[]).append(d)
    for seg,creators in segs.items():
        avg=sum(c["brand_fit_score"] for c in creators)//len(creators)
        reach=sum(c["followers"] for c in creators)
        collabs=list(set(c["collaboration_recommended"] for c in creators))
        st.markdown(f"""<div class='card card-accent'>
<div style='font-weight:600;font-size:.95rem;margin-bottom:10px'>{seg} — {len(creators)} creator{"s" if len(creators)>1 else ""}</div>
<div style='display:flex;gap:16px;margin-bottom:10px'>
  <div style='background:#e8f5fb;border-radius:8px;padding:8px 14px;flex:1;text-align:center'><div style='color:#45b3e0;font-weight:700'>{avg}%</div><div style='color:#5a8fa0;font-size:.72rem'>Avg. Fit Score</div></div>
  <div style='background:#e8f5fb;border-radius:8px;padding:8px 14px;flex:1;text-align:center'><div style='color:#45b3e0;font-weight:700'>{ffmt(reach)}</div><div style='color:#5a8fa0;font-size:.72rem'>Combined Reach</div></div>
  <div style='background:#e8f5fb;border-radius:8px;padding:8px 14px;flex:1;text-align:center'><div style='color:#45b3e0;font-weight:700'>{', '.join(collabs)}</div><div style='color:#5a8fa0;font-size:.72rem'>Recommended Collab</div></div>
</div>
<div style='color:#5a8fa0;font-size:.8rem'>Creators: {", ".join(c["creator_handle"] for c in creators)}</div>
</div>""",unsafe_allow_html=True)

def main():
    st.markdown(CSS,unsafe_allow_html=True)
    if "results" not in st.session_state: st.session_state.results=None
    run,clr,bn,ind,kw,tone,max_creators,brief,fr=sidebar()
    
    if clr: st.session_state.results=None
    
    if run:
        if not kw:
            st.error("Please enter Target Keywords to run discovery.")
        else:
            ph=st.empty()
            with ph.container(): stepper(0)
            yt = YouTubeDiscovery()
            ig = InstagramDiscovery()
            y_inf = yt.search_influencers(kw, max_results=30, min_followers=fr[0], max_followers=fr[1])
            i_inf = ig.search_influencers(kw)
            infs = (y_inf + i_inf)[:max_creators]
            
            if not infs:
                st.error("No influencers found.")
                ph.empty()
            else:
                with ph.container(): stepper(1)
                time.sleep(0.5)
                
                with ph.container(): stepper(2)
                print_banner(kw, bn or "[Brand]", 5)
                analyzer = ContentAnalyzer(brand_name=bn)
                for d in infs:
                    analyzer.analyze(d)
                    print_analysis_result(d['name'], d)
                
                with ph.container(): stepper(3)
                scorer = BrandFitScorer()
                for d in infs: scorer.calculate_score(d)
                
                with ph.container(): stepper(4)
                outreach = OutreachGenerator(bn, tone, ind, brief)
                for d in infs:
                    outreach.generate(d)
                    if d.get('outreach'):
                        print_outreach_preview(d['name'], d['outreach'])
                
                for d in infs:
                    d['creator_handle'] = d.get('handle', d.get('name'))
                    d['followers'] = d.get('follower_count', 0)
                    d['fit_explanation'] = d.get('reasoning', "Good fit overall.")
                    
                    # Calculate engagement rate: avg views / subscribers * 100
                    v = int(d.get('metadata',{}).get('view_count') or 0)
                    vc = int(d.get('metadata',{}).get('video_count') or 1)
                    subs = d.get('follower_count', 1)
                    avg_v = v // vc if vc else 0
                    d['avg_views'] = avg_v
                    d['engagement_rate'] = round((avg_v / subs * 100), 1) if subs else 3.5
                    
                    # Estimate posting frequency from total video count
                    if vc >= 500: d['posting_frequency'] = "Daily"
                    elif vc >= 200: d['posting_frequency'] = "3-4x/week"
                    elif vc >= 100: d['posting_frequency'] = "2x/week"
                    elif vc >= 50: d['posting_frequency'] = "Weekly"
                    else: d['posting_frequency'] = "Occasional"
                    if 'engagement_quality' not in d: d['engagement_quality'] = "Genuine"
                    if 'engagement_reason' not in d: d['engagement_reason'] = "Consistent organic growth."
                    if 'growth_trend' not in d: d['growth_trend'] = "Stable"
                    if 'brand_fit_score' not in d: d['brand_fit_score'] = d.get('relevance_score', 50)
                    if 'niche' not in d: d['niche'] = "General"
                    if 'segment_name' not in d: d['segment_name'] = "Segment A: General Audience"
                    if 'content_themes' not in d: d['content_themes'] = ["Video Content"]
                    if 'recent_signals' not in d: d['recent_signals'] = ["Recent upload"]
                    if 'collaboration_recommended' not in d: d['collaboration_recommended'] = d.get('recommended_collab_type', "Barter")
                    if 'outreach' in d:
                        d['email_body'] = d['outreach'].get('email', '')
                        d['dm_message'] = d['outreach'].get('dm', '')
                    else:
                        d['email_body'] = ''
                        d['dm_message'] = ''
                    d['email_subject'] = f"Partnership Opportunity — {bn} x {d.get('handle', '')}"
                    
                    if 'outreach_signals_used' not in d: d['outreach_signals_used'] = "Recent channel activity"
                    if 'contact_email' not in d: d['contact_email'] = "Not listed"
                    if 'competitor_flag' not in d: d['competitor_flag'] = False
                    if 'competitor_detail' not in d: d['competitor_detail'] = None

                Exporter.save_run(infs)
                st.session_state.results = infs
                ph.empty()

    if st.session_state.results is None:
        hero()
    else:
        data=st.session_state.results
        st.markdown("<br>",unsafe_allow_html=True)
        metrics(data)
        st.markdown("<br>",unsafe_allow_html=True)
        t1,t2,t3,t4,t5=st.tabs(["Creator Profiles","Comparison Table","Content Intelligence","Outreach Manager","Campaign Strategy"])
        with t1: tab_profiles(data, bn)
        with t2: tab_table(data)
        with t3: tab_intel(data)
        with t4: tab_outreach(data)
        with t5: tab_strategy(data,bn,ind)
        
    st.markdown("<div class='foot'>OutreachOS — Influencer Intelligence Platform | Built for modern brand outreach teams</div>",unsafe_allow_html=True)

if __name__ == "__main__":
    main()
