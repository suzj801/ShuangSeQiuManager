import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

db = sqlalchemy.create_engine('sqlite:///balls.db')
Session = sessionmaker(bind=db)
Base = declarative_base()

class WinningLevel(Enum):
    Level0 = (0, "未中奖")
    Level1 = (1, "一等奖")
    Level2 = (2, "二等奖")
    Level3 = (3, "三等奖")
    Level4 = (4, "四等奖")
    Level5 = (5, "五等奖")
    Level6 = (6, "六等奖")
    
    def __init__(self, value, description):
        self._value = value
        self._description = description

    @property
    def value(self):
        return self._value

    @property
    def description(self):
        return self._description
    
class BallBlueColumn(sqlalchemy.Column):
    def __init__(self):
        super(BallBlueColumn, self).__init__(sqlalchemy.Integer, sqlalchemy.CheckConstraint('ballBlue >= 1 and ballBlue <= 16'), nullable=False)

class BallRedColumn(sqlalchemy.Column):
    def __init__(self):
        super(BallRedColumn, self).__init__(sqlalchemy.Integer, sqlalchemy.CheckConstraint('ballRed >= 1 and ballRed <= 33'), nullable=False)


class LotteryBalls(Base):
    __tablename__ = 'lotteryBalls'
    ballsId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    lotteryNo = sqlalchemy.Column(sqlalchemy.String(10), nullable=False)   #期数
    ballBlue = BallBlueColumn()
    ballRed1 = BallRedColumn()
    ballRed2 = BallRedColumn()
    ballRed3 = BallRedColumn()
    ballRed4 = BallRedColumn()
    ballRed5 = BallRedColumn()
    ballRed6 = BallRedColumn()
    lotteryDate = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    addData = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.today())

    @classmethod
    def add_balls(cls, balls):
        with Session() as session:
            if existBalls := session.query(cls).where(cls.lotteryNo == balls['lotteryNo']).first():
                existBalls.addData = datetime.today()
                existBalls.ballBlue = balls['blue']
                existBalls.ballRed1, existBalls.ballRed2, existBalls.ballRed3, \
                    existBalls.ballRed4, existBalls.ballRed5, existBalls.ballRed6= balls['red']
            else:
                _lotteryBalls = cls()
                _lotteryBalls.lotteryNo = balls['lotteryNo']
                _lotteryBalls.ballRed1, _lotteryBalls.ballRed2, _lotteryBalls.ballRed3, \
                    _lotteryBalls.ballRed4, _lotteryBalls.ballRed5, _lotteryBalls.ballRed6= balls['red']
                _lotteryBalls.ballBlue = balls['blue']
                _lotteryBalls.lotteryDate = balls['lotteryDate']
                session.add(_lotteryBalls)
            session.commit()

    @classmethod
    def get_newest_lotteryno(cls):
        with Session() as session:
            newestRow = session.query(cls).order_by(cls.lotteryNo.desc()).first()
            if newestRow:
                return newestRow.lotteryNo
            else:
                return ""
    
    @classmethod
    def get_balls_freq(cls):
        #取出现次数
        freqs = {"blue":{i:0 for i in range(1, 17)}, "red":{i:0 for i in range(1, 34)}}
        with Session() as session:
            for row in session.query(cls):
                freqs['blue'][row.ballBlue] += 1
                freqs['red'][row.ballRed1] += 1
                freqs['red'][row.ballRed2] += 1
                freqs['red'][row.ballRed3] += 1
                freqs['red'][row.ballRed4] += 1
                freqs['red'][row.ballRed5] += 1
                freqs['red'][row.ballRed6] += 1
        return freqs
    
    @classmethod
    def get_balls_continuity(cls):
        #取连续次数
        continuity = {"blue":{i:0 for i in range(1, 17)}, "red":{i:0 for i in range(1, 34)}}
        lastRow = None
        with Session() as session:
            for row in session.query(cls).order_by(cls.lotteryDate):
                if lastRow:
                    if row.ballBlue == lastRow.ballBlue:
                        continuity['blue'][row.ballBlue] += 1
                    for ball in set([row.ballRed1, row.ballRed2, row.ballRed3, row.ballRed4,
                                    row.ballRed5, row.ballRed6]) & set([lastRow.ballRed1, lastRow.ballRed2,
                                    lastRow.ballRed3, lastRow.ballRed4, lastRow.ballRed5, lastRow.ballRed6]):
                        continuity['red'][ball] += 1
                lastRow = row
        return continuity

class PaidBalls(Base):
    __tablename__ = 'paidBalls'
    ballsId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    lotteryNo = sqlalchemy.Column(sqlalchemy.String(10), nullable=False)
    ballBlue = BallBlueColumn()
    ballRed1 = BallRedColumn()
    ballRed2 = BallRedColumn()
    ballRed3 = BallRedColumn()
    ballRed4 = BallRedColumn()
    ballRed5 = BallRedColumn()
    ballRed6 = BallRedColumn()
    paidDate = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    checked = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    winningLevel = sqlalchemy.Column(sqlalchemy.Enum(WinningLevel), default=WinningLevel.Level0)
    checkedDate = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    addData = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.today())

    @classmethod
    def add_balls(cls, balls):
        with Session() as session:
            _paidBalls = cls()
            _paidBalls.lotteryNo = balls['lotteryNo']
            _paidBalls.ballRed1, _paidBalls.ballRed2, _paidBalls.ballRed3, \
                _paidBalls.ballRed4, _paidBalls.ballRed5, _paidBalls.ballRed6= balls['red']
            _paidBalls.ballBlue = balls['blue']
            _paidBalls.paidDate = balls.get('paidDate', datetime.today())
            _paidBalls.checked = False
            _paidBalls.winningLevel = WinningLevel.Level0
            session.add(_paidBalls)
            session.commit()

    @classmethod
    def check_lottery(cls):
        winningBalls = {}
        checkedRows = []
        with Session() as session:
            for row in session.query(cls).where(cls.checked == False).order_by(cls.paidDate):
                if row.lotteryNo not in winningBalls:
                    _winningBalls = session.query(LotteryBalls).where(LotteryBalls.lotteryNo == row.lotteryNo).first()
                    if not _winningBalls:
                        winningBalls[row.lotteryNo] = None
                    else:
                        winningBalls[row.lotteryNo] = {'blue': _winningBalls.ballBlue,
                                                    'red': set([_winningBalls.ballRed1,
                                                            _winningBalls.ballRed2,
                                                            _winningBalls.ballRed3,
                                                            _winningBalls.ballRed4,
                                                            _winningBalls.ballRed5,
                                                            _winningBalls.ballRed6])} #set利于匹配
                if not winningBalls[row.lotteryNo]: #这期没有录入或者没有开奖
                    continue
                _balls = {'blue': row.ballBlue, 'red': set([row.ballRed1, row.ballRed2, row.ballRed3, row.ballRed4, row.ballRed5, row.ballRed6])}
                redMatched = _balls['red'] & winningBalls[row.lotteryNo]['red']
                blueMatched = _balls['blue'] == winningBalls[row.lotteryNo]['blue']
                if len(redMatched) == 6:
                    if blueMatched:
                        row.winningLevel = WinningLevel.Level1
                    else:
                        row.winningLevel = WinningLevel.Level2
                elif len(redMatched) == 5:
                    if blueMatched:
                        row.winningLevel = WinningLevel.Level3
                    else:
                        row.winningLevel = WinningLevel.Level4
                elif len(redMatched) == 4:
                    if blueMatched:
                        row.winningLevel = WinningLevel.Level4
                    else:
                        row.winningLevel = WinningLevel.Level5
                elif len(redMatched) == 3 and blueMatched:
                    row.winningLevel = WinningLevel.Level5
                elif blueMatched:
                    row.winningLevel = WinningLevel.Level6
                else:
                    row.winningLevel = WinningLevel.Level0
                row.checked = True
                checkedRows.append(row_to_dict(row))
                session.commit()
        return checkedRows
    
    @classmethod
    def get_balls(cls, filterBy):
        with Session() as session:
            return [row_to_dict(row) for row in session.query(cls).filter_by(**filterBy)]

def initDB():
    Base.metadata.create_all(db)

def row_to_dict(row):
    d = {}
    for column in row.__table__.columns:
        if isinstance(column.type, sqlalchemy.DateTime):
            d[column.name] = getattr(row, column.name).strftime('%Y年%m月%d日') if getattr(row, column.name) else None
        elif isinstance(column.type, sqlalchemy.Enum):
            d[column.name] = getattr(row, column.name).description if row.checked else "未出奖"
        else:
            d[column.name] = getattr(row, column.name)
    return d

def print_all_data(model):
    with Session() as session:
        for row in session.query(model):
            print(row_to_dict(row))

if __name__ == '__main__':
    #print_all_data(LotteryBalls)
    print_all_data(PaidBalls)