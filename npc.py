import uuid, random
class NPC:
    def __init__(self, name, age=0, gender=None, uid=None):
        self.uid = uid or str(uuid.uuid4())
        self.name = name
        self.age = age
        self.gender = gender or random.choice(['M','F','Nonbinary'])
        self.trust, self.knowledge, self.job = {}, [], 'unassigned'
        self.alive, self.partner_uid, self.children_uids = True, None, []
    def to_dict(self):
        return {
            'uid': self.uid, 'name': self.name, 'age': self.age, 'gender': self.gender,
            'trust': self.trust, 'knowledge': self.knowledge, 'job': self.job,
            'alive': self.alive, 'partner_uid': self.partner_uid, 'children_uids': self.children_uids
        }
    @classmethod
    def from_dict(cls, d):
        n = cls(d.get('name','NPC'), d.get('age',0), d.get('gender'), d.get('uid'))
        n.trust = d.get('trust', {})
        n.knowledge = d.get('knowledge', [])
        n.job = d.get('job', 'unassigned')
        n.alive = d.get('alive', True)
        n.partner_uid = d.get('partner_uid')
        n.children_uids = d.get('children_uids', [])
        return n
    def tick_year(self):
        if not self.alive: return False
        self.age += 1
        base = 0.005
        if self.age > 60: base += (self.age-60)*0.01
        if random.random() < base:
            self.alive = False
            return True
        return False
    def learn(self, skill):
        if skill not in self.knowledge: self.knowledge.append(skill)
    def share_knowledge_with(self, other):
        if not self.knowledge: return None
        skill = random.choice(self.knowledge)
        other.learn(skill); return skill
