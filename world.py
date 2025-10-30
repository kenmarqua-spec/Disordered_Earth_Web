import random, os
from npc import NPC
from save_system import SaveManager
class World:
    def __init__(self, save_manager=None, autosave_years=1):
        self.save_manager = save_manager or SaveManager()
        self.autosave_years = autosave_years
        self.year = 0; self.npcs = {}; self.world_knowledge = []; self.stats = {'births':0,'deaths':0,'marriages':0}
        if self.save_manager.exists():
            self._load_from_save()
        else:
            self._initialize_new_world()
    def _initialize_new_world(self):
        starter = ['Ari','Brek','Chal','Dune','Ena','Faro','Gim']
        for n in starter:
            npc = NPC(n, age=random.randint(16,40))
            if random.random() < 0.5: npc.learn('basic_toolmaking')
            self.npcs[npc.uid] = npc
        self.world_knowledge = ['basic_toolmaking']
        self.year = 1; self._save('initial')
    def _load_from_save(self):
        data = self.save_manager.load()
        if not data: return
        payload = data.get('payload',{})
        self.year = payload.get('year',1)
        self.world_knowledge = payload.get('world_knowledge',[])
        self.stats = payload.get('stats',{'births':0,'deaths':0,'marriages':0})
        self.npcs = {d['uid']: NPC.from_dict(d) for d in payload.get('npcs',[])}
        print(f"[World] Loaded year {self.year} pop {len(self.npcs)}")
    def _serialize(self):
        return {'year':self.year,'world_knowledge':self.world_knowledge,'stats':self.stats,'npcs':[n.to_dict() for n in self.npcs.values()]}
    def _save(self, reason=None):
        self.save_manager.save(self._serialize())
        if reason: print(f"[Save] Year {self.year} saved ({reason}). Pop {len(self.npcs)}")
    def tick_year(self):
        self.year += 1; major=False; deaths=[]
        for npc in list(self.npcs.values()):
            if npc.tick_year(): deaths.append(npc.uid)
        for uid in deaths:
            self.stats['deaths']+=1
            npc = self.npcs.get(uid)
            if npc and npc.partner_uid and npc.partner_uid in self.npcs:
                self.npcs[npc.partner_uid].partner_uid = None
            if uid in self.npcs: del self.npcs[uid]
            major=True
        adults = [n for n in self.npcs.values() if n.age>=16 and n.alive]
        random.shuffle(adults)
        for n in adults:
            if n.partner_uid and random.random()<0.10:
                child = NPC('Child'+str(self.year), age=0)
                self.npcs[child.uid]=child; self.stats['births']+=1
                major=True
        if random.random()<0.03:
            singles = [p for p in self.npcs.values() if p.partner_uid is None and p.age>=18]
            if len(singles)>=2:
                a,b = random.sample(singles,2); a.partner_uid=b.uid; b.partner_uid=a.uid; self.stats['marriages']+=1; major=True
        for npc in self.npcs.values():
            if npc.knowledge and random.random()<0.2:
                others=[o for o in self.npcs.values() if o.uid!=npc.uid]
                if others:
                    other=random.choice(others); learned=npc.share_knowledge_with(other)
                    if learned and learned not in self.world_knowledge: self.world_knowledge.append(learned); major=True
        if random.random()<0.01:
            new='recipe_'+str(self.year); self.world_knowledge.append(new); random.choice(list(self.npcs.values())).learn(new); major=True
        if self.year % self.autosave_years==0 or major:
            self._save('autosave' if self.year%self.autosave_years==0 else 'event_save')
    def get_stats(self):
        return {'year':self.year,'population':len(self.npcs),'world_knowledge_count':len(self.world_knowledge), **self.stats}
    def force_save(self, reason='manual'): self._save(reason)
