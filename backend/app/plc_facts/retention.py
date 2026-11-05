"""上海墙上时间+纳秒尾数与自然月截止；无宿主时区依赖。"""
import calendar
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re
from .error_codes import FactsError
SHANGHAI=timezone(timedelta(hours=8))
_PATTERN=re.compile(r'^(\d{4}-\d\d-\d\d)[Tt](\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?([Zz]|[+-]\d\d:\d\d)$')

@dataclass(frozen=True,order=True)
class Instant:
    wall: datetime
    ns: int=0
    def wire(self):
        return self.wall.strftime('%Y-%m-%dT%H:%M:%S')+'.%06d%03d+08:00'%(self.wall.microsecond,self.ns)
    def months(self,count):
        year,month=divmod(self.wall.year*12+self.wall.month-1+count,12); month+=1
        if not 1000<=year<=9999: raise FactsError('invalid_request')
        return Instant(self.wall.replace(year=year,month=month,day=min(self.wall.day,calendar.monthrange(year,month)[1])),self.ns)
    def seconds(self,count): return Instant(self.wall+timedelta(seconds=count),self.ns)

def instant(value):
    if not isinstance(value,str): raise FactsError('invalid_request')
    m=_PATTERN.fullmatch(value)
    if not m: raise FactsError('invalid_request')
    date,time,fraction,offset=m.groups(); fraction=(fraction or '').ljust(9,'0')
    try:
        if offset.lower()=='z': offset='+00:00'
        if int(offset[1:3])>23 or int(offset[4:6])>59: raise ValueError()
        dt=datetime.fromisoformat(date+'T'+time+'.'+fraction[:6]+offset).astimezone(SHANGHAI).replace(tzinfo=None)
        if dt.year<1000: raise ValueError()
        return Instant(dt,int(fraction[6:]))
    except (ValueError,OverflowError): raise FactsError('invalid_request') from None

def wire(value): return instant(value).wire()
def db_instant(value): return Instant(value.replace(tzinfo=None))
def expiry(observed,months):
    if months not in (1,2,3): raise FactsError('not_ready',503)
    return instant(observed).months(months)
def proof_expiry(now): return now.seconds(120*86400)
