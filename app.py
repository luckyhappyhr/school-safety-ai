import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings

# 파이썬 경고 메시지 완벽 차단
warnings.filterwarnings('ignore')

# ⚙️ 페이지 기본 설정 (가장 먼저 호출되어야 함)
st.set_page_config(page_title="4D 학교 안전 큐레이션 AI", layout="wide", page_icon="🧠")

# ==========================================
# 1. 핵심 AI 진단 클래스 및 데이터베이스
# ==========================================
class GeniusSafetyDiagnosticUltimate:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.baselines = {}
        self.prefixes = {
            '행동': '행동-', '활동': '활동-', '장소': '장소-', '형태': '형태-'
        }
        self.all_categories = {'행동': [], '활동': [], '장소': [], '형태': []}
        self.severe_accidents = [
            '화학물질 노출', '열, 전기에 의한 손상', '끼임·눌림', '식중독 및 이물질 섭취, 접촉',
            '(교통수단 등) 운전, 조작, 탑승 중', '교통구역(스쿨존 내)', '교통구역(스쿨존 외)'
        ]

        # 🩺 [보건실 전용] 사고 키워드별 필수 비축 물품 DB (원본 유지)
        self.medical_supply_db = {
            '염좌': "냉찜질팩, 압박붕대, 뿌리는 파스, 부목",
            '삐임': "냉찜질팩, 압박붕대, 뿌리는 파스, 부목",
            '부딪': "치과 응급처치 세트, 치아 보존액, 얼음주머니, 외상 연고",
            '긁힘': "소독약, 드레싱 밴드, 지혈제, 거즈",
            '찔림': "소독약, 드레싱 밴드, 지혈제, 거즈",
            '베임': "소독약, 드레싱 밴드, 지혈제, 거즈",
            '절단': "지혈대, 멸균 생리식염수, 지혈 패드",
            '열': "화상 쿨링 시트, 화상 연고, 멸균 거즈",
            '전기': "화상 쿨링 시트, 화상 연고, 멸균 거즈",
            '낙상': "찰과상 연고, 습윤 드레싱, 탄력 붕대",
            '떨어짐': "찰과상 연고, 습윤 드레싱, 탄력 붕대",
            '식중독': "비상 제산제, 소화제, 구토용 위생봉투",
            '화학': "생리식염수(안구 세척용), 중화제, 보호 안경",
            '육상': "냉찜질팩, 압박붕대, 찰과상 연고",
            '구기': "치과 응급처치 세트, 얼음주머니, 압박붕대",
            '체조': "압박붕대, 파스, 얼음찜질 팩",
            '수중': "응급 보온포, 산소 캔, 인공호흡 마스크",
            '무도': "얼음찜질 팩, 탄력 붕대, 타박상 연고",
            '싸움': "심리 안정 지원 공간, 타박상 연고, 얼음주머니",
            '기타': "일반 밴드, 알코올 스왑, 다목적 소독제"
        }

        # 🧠 [부서별 역할 분리 & 맞춤 영상 링크 DB] (원본 유지)
        self.solutions_db = {
            '일반학습': {
                '담임': "교실 내 필기구 및 책상 모서리 안전 가드 부착 및 수업 전 1분 정리 정돈 퀘스트", '행정실': "사물함 고정 상태 및 칠판/모니터 부착 상태 긴급 점검", '보건실': "교실 내 찰과상 응급처치 매뉴얼 안내", 
                'videos': {
                    '초등': [("문을 열고 닫을 때는 주위를 살펴요", "https://www.youtube.com/watch?v=bIq3lV2Ubgk"), ("(일반) 교실 이용시 주의할 점 알아보기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2866")],
                    '중학': [("(일반) 교실의 시설(액자, 게시판, 책상, 의자 등) 안전하게 활용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2737")],
                    '고등': [("(일반) 교실의 시설(액자, 게시판, 책상, 의자 등) 안전하게 활용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2737")],
                    '공통': []
                }
            },
            '걷기/뛰기, 오르내리기': {
                '담임': "계단 1줄 서기 및 1칸씩 내려가기 생활화 지도", '행정실': "복도 착시 아트 스티커 부착으로 무의식적 감속 유도(넛지)", '보건실': "시간대별 환자 추이 분석 및 교직원 안전 협의회 안건 상정", 
                'videos': {
                    '초등': [("[초등 4~6학년] 복도와 계단을 안전하게 이용해요", "https://www.youtube.com/watch?v=etXkcCEQi7E")],
                    '중학': [("[중학교] 안전한 실내, 복도와 계단 사용법", "https://www.youtube.com/watch?v=sgOIyHjYzTg")],
                    '고등': [("[고등학교] 학교 복도와 계단에서는 조심해서 다녀요!", "https://www.youtube.com/watch?v=wLJj32FPZPI")],
                    '공통': [("[매일 5분 안전교실] 학교 내 사고예방교육", "https://www.youtube.com/watch?v=A0f7nDThctY")]
                }
            },
            '씻기': {
                '담임': "화장실 바닥 물기 주의 및 뛰지 않기 철저 지도", '행정실': "화장실 바닥 미끄럼 방지 타일 시공 및 온수 온도 고정 장치 점검", '보건실': "미끄러짐으로 인한 타박상 및 치아 손상 응급 매뉴얼 정비",
                'videos': {
                    '초등': [("[초등학교] (화면해설) 화장실 안전하게 사용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=3648")],
                    '중학': [("(일반) 화장실 안전하게 사용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2854"), ("(일반) 화장실 감전사고 예방법 알아보기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2996")],
                    '고등': [("(일반) 화장실 안전하게 사용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2854"), ("(일반) 화장실 감전사고 예방법 알아보기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2996")],
                    '공통': []
                }
            },
            '구기': {
                '담임': "신체 접촉 최소화를 위한 변형 룰(언택트 수비) 도입", '행정실': "이동식 팝업 펜스를 활용한 운동장 구획 분할 지원", '보건실': "염좌 및 손가락 부상 다빈도 예측 및 대응", 
                'videos': {
                    '초등': [("체육활동을 안전하게 즐겨요", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=4805")],
                    '중학': [("[중학교] 안전수칙을 지켜요! 즐거운 체육·스포츠 활동", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=4825")],
                    '고등': [("[고등학교] 구기종목 체육시간 안전하게 활동해요", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=4847")],
                    '공통': [("학교 활동 중 안전사고가 가장 많이 발생하는 체육시간! 이것만은 꼭 지켜요", "https://www.youtube.com/watch?v=8GwCv1SCxZk")]
                }
            },
            '육상': {
                '담임': "트랙 진입 전 '필수 웜업 퀘스트' 통과 및 전용 신발 착용 지도", '행정실': "트랙 규사 보충 및 미끄럼 방지 논슬립 코팅 재시공", '보건실': "육상 수업 시 구급함 전진 배치 체계화", 
                'videos': {
                    '초등': [("체육활동을 안전하게 즐겨요", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=4805")],
                    '중학': [("[중학교] 안전수칙을 지켜요! 즐거운 체육·스포츠 활동", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=4825")],
                    '고등': [("[고등학교] 구기종목 체육시간 안전하게 활동해요", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=4847")],
                    '공통': [("학교 활동 중 안전사고가 가장 많이 발생하는 체육시간! 이것만은 꼭 지켜요", "https://www.youtube.com/watch?v=8GwCv1SCxZk")]
                }
            },
            '체조·무용·매트운동': {
                '담임': "착지 지점 안전 매트 2중 보강 및 유연성 확보 스트레칭 도입", '행정실': "매트 오염 및 손상 부위 교체", '보건실': "인대 늘어남 등 다빈도 부상 맵핑", 
                'videos': {
                    '초등': [("체조 활동 사고 예방방법", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2142")],
                    '중학': [("(일반) 창문을 통한 낙상, 떨어짐, 추락사고 예방하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2853")],
                    '고등': [("(일반) 창문을 통한 낙상, 떨어짐, 추락사고 예방하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2853")],
                    '공통': []
                }
            },
            '낙상': {
                '담임': "낙상 예방 '낙법 기초' 체험 교육 및 실내 뛰지 않기 캠페인", '행정실': "계단 모서리 논슬립 패드 전면 교체 및 복도 마찰력 증대 시공", '보건실': "낙상 사고 핫스팟 맵핑 및 중증도 타박상 응급 매뉴얼 점검", 
                'videos': {
                    '초등': [("놀이기구 추락 및 끼임 사고", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2665"), ("운동장과 놀이터에서 안전하게 놀아요", "https://www.youtube.com/watch?v=ULrnfqE56Zs")],
                    '중학': [("(일반) 창문을 통한 낙상, 떨어짐, 추락사고 예방하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2853")],
                    '고등': [("(일반) 창문을 통한 낙상, 떨어짐, 추락사고 예방하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2853")],
                    '공통': []
                }
            },
            '휴식': {
                '담임': "교실 및 복도 내 사각지대 장난 금지 및 안전한 놀이 방법 안내", '행정실': "창문 추락 방지 바 및 복도 모서리 안전 가드 점검", '보건실': "쉬는 시간 다빈도 발생 찰과상 및 타박상 신속 처치 준비",
                'videos': {
                    '초등': [("안전캠페인 쉬는시간안전 3분", "https://www.youtube.com/watch?v=u7e6z3UIJkA"), ("쉬는시간 사고 예방, 꼭 알아야 할 안전수칙", "https://www.youtube.com/watch?v=KCX2-5MRgu0")],
                    '중학': [("운동장 학교안전", "https://www.youtube.com/watch?v=cGhnN4RQA8s")],
                    '고등': [("운동장 학교안전", "https://www.youtube.com/watch?v=cGhnN4RQA8s")],
                    '공통': []
                }
            },
            '장난, 놀이': {
                '담임': "교실 및 복도 내 사각지대 장난 금지 및 안전한 놀이 방법 안내", '행정실': "창문 추락 방지 바 및 복도 모서리 안전 가드 점검", '보건실': "쉬는 시간 다빈도 발생 찰과상 신속 처치 준비",
                'videos': {
                    '초등': [("안전캠페인 쉬는시간안전 3분", "https://www.youtube.com/watch?v=u7e6z3UIJkA"), ("쉬는시간 사고 예방, 꼭 알아야 할 안전수칙", "https://www.youtube.com/watch?v=KCX2-5MRgu0")],
                    '중학': [("운동장 학교안전", "https://www.youtube.com/watch?v=cGhnN4RQA8s")],
                    '고등': [("운동장 학교안전", "https://www.youtube.com/watch?v=cGhnN4RQA8s")],
                    '공통': []
                }
            },
            '교통구역(스쿨존 내)': {
                '담임': "창체시간 활용 스쿨존 보행수칙(스몸비 방지) 필수 교육", '행정실': "교문 앞 옐로카펫 재도색 및 반사경(사각지대) 각도 조정", '보건실': "아차사고(Near-miss) 사례 수집 및 예방 캠페인 주도", 
                'videos': {
                    '초등': [("<안전채널e> 7화 - 스쿨보이가 들려준 이야기(스쿨존편)", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2453")],
                    '중학': [("생활 속 숨어 있는 스마트폰의 위험성", "https://www.youtube.com/watch?v=iYMp2W3YJpE")],
                    '고등': [("생활 속 숨어 있는 스마트폰의 위험성", "https://www.youtube.com/watch?v=iYMp2W3YJpE")],
                    '공통': []
                }
            },
            '(교통수단 등) 운전, 조작, 탑승 중': {
                '담임': "자전거 및 킥보드 탑승 시 헬멧 착용 등 개인형 이동장치 안전 교육", '행정실': "교내 자전거 보관소 주변 안전 펜스 및 주차 구역 정비", '보건실': "아스팔트 찰과상 및 골절 대비 응급 키트 점검",
                'videos': {
                    '초등': [("[초등 1~3학년] 자전거 등교 시 사고 유형에 따른 안전한 자전거 이용", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2833")],
                    '중학': [("[중학교] 자전거 등교시 사고 유형에 따른 안전한 자전거 이용", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2858")],
                    '고등': [("[고등학교] 자전거 이용한 등·하교 시 안전수칙 토론하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=3017")],
                    '공통': []
                }
            },
            '긁힘·베임·절단·찔림': {
                '담임': "미술, 실과 시간 칼/가위 등 날카로운 도구 사용 전 안전수칙 지도", '행정실': "노후화된 책걸상 모서리 및 날카로운 시설물 전수 점검", '보건실': "외상 처치 물품 소진량 파악 및 신속 보충",
                'videos': {
                    '초등': [("[초등 1~3학년] 미술도구를 안전하게 이용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2748"), ("[초등 4~6학년] 실과수업 시 바늘, 가위 등 안전하게 이용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2733")],
                    '중학': [],
                    '고등': [],
                    '공통': [("[응급처치] 외상에 의한 출혈을 멈추는 가장 좋은 방법", "https://www.youtube.com/watch?v=4yE4zPzrSwM"), ("뾰족한 물건에 찔렸을 때 올바른 응급처치법", "https://www.youtube.com/watch?v=8tjC9Rram24")]
                }
            },
            '화학물질 노출': {
                '담임': "실험 전 물질안전보건자료(MSDS) 숙지 및 보호안경 착용 필수화", '행정실': "과학실 비상 안구 세척기 비치 및 환기 시설 집중 점검", '보건실': "화학물질 피부/안구 노출 시 긴급 응급처치 매뉴얼 가동", 
                'videos': {
                    '초등': [("[초등 1~3학년] 과학실 안전하게 이용하는 방법 알아보기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2747")],
                    '중학': [],
                    '고등': [],
                    '공통': [("갈등과학실험실 응급상황 대처법", "https://www.youtube.com/watch?v=m5oJaW0orvk")]
                }
            },
            '식사': {
                '담임': "급식실 이동 시 질서 유지 및 뜨거운 국물 배식 주의 지도", '행정실': "급식실 바닥 미끄럼 방지 매트 설치 및 배식 카트 안전 점검", '보건실': "열탕 화상 발생 대비 신속 대응 체계화",
                'videos': {
                    '초등': [("[초등 4~6학년] 식당과 급식실 안전하게 이용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2826")],
                    '중학': [("[중학교] 급식실 안전하게 이용하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=2856")],
                    '고등': [("[고등학교] 급식실 이용수칙 실천하여 안전사고 예방하기", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=3015")],
                    '공통': []
                }
            },
            '싸움': {
                '담임': "교우 관계 관찰 강화 및 갈등 발생 시 초기 개입 및 상담", '행정실': "학교 폭력 사각지대(CCTV 미설치 구역) 순찰 강화 및 조명 개선", '보건실': "신체 폭력 피해 학생의 심리적 안정 지원 및 외상 치료",
                'videos': {
                    '초등': [], '중학': [], '고등': [],
                    '공통': [("<안전채널e> 23화 - 학교 폭력 부메랑(2021)", "https://www.schoolsafe24.or.kr/front/rpstr/selectRpstrInfo.do?menuSn=185&upperMenuSn=148&rpstrPstSn=1974")]
                }
            },
            '부딪힘(교통사고 포함)': {'담임': "교실 및 복도 우측통행 생활화 및 사각지대 뛰지 않기 지도", '행정실': "코너 구역 '일단 정지' 바닥 픽토그램 도색 및 충격흡수 가드 부착", '보건실': "충돌 사고 빈발 시간대(쉬는시간, 점심) 예방 순찰 강화"},
            '끼임·눌림': {'담임': "문 열고 닫을 때 손잡이 사용 및 장난 금지 철저 지도", '행정실': "교실 문 틈새 방지 가드 100% 설치 및 사물함 '소프트 클로징' 교체", '보건실': "골절 및 찰과상 등 다빈도 응급처치 교육"},
            '무도': {'담임': "충격 흡수용 고밀도 매트 상시 배치 및 급소 보호 장구 착용 의무화", '행정실': "안전 매트 상태 점검 및 추가 구매 지원", '보건실': "타박상 대응 매뉴얼 갱신"},
            '수중': {'담임': "입수 전 심박수 체크 및 체온 유지용 래쉬가드 착용 지도", '행정실': "수영장 바닥 미끄럼 방지 점검 및 샤워시설 온수 확인", '보건실': "저체온증 및 익수 사고 대비 모니터링"},
            '체육·집회공간': {'담임': "강당 진입 시 질서 유지 및 시설물 임의 조작 금지 교육", '행정실': "벽면 충격 흡수 패드 전면 시공 및 소화기 가시성 확보", '보건실': "다수 밀집 시 발생 가능한 안전사고 예방 점검"},
        }

    def get_default_solution(self, item):
        return {
            '담임': f"'{item}' 발생 구역의 학생 밀집도 분산 및 생활 지도 강화",
            '행정실': f"해당 구역 환경적 위험 요인 긴급 점검 및 물리적 시설 보완",
            '보건실': f"관련 응급처치 매뉴얼 정비 및 교직원 비상 연락망 점검",
            'videos': {
                '초등': [], '중학': [], '고등': [],
                '공통': [(f"'{item}' 맞춤형 안전 교육 영상", f"https://www.youtube.com/results?search_query=학교+안전사고+{item}")]
            }
        }

# ==========================================
# 2. 전역 함수 (Streamlit 캐싱 적용으로 성능 향상)
# ==========================================
@st.cache_data
def load_data_and_compute_baselines(csv_path):
    app = GeniusSafetyDiagnosticUltimate(csv_path)
    try:
        # 1. 파일 읽기 및 컬럼 정리
        df = pd.read_csv(app.csv_file_path)
        df.columns = df.columns.str.replace('\n', '').str.replace('\r', '').str.strip()
        df = df.ffill()
        
        # 2. 모든 데이터 강제 숫자 변환 (핵심 에러 방지 구역)
        for col in df.columns:
            if col not in ['구분', '학교급']:
                # 문자가 섞인 데이터를 강제로 숫자로 변환 (실패 시 0 처리)
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(',', '').str.replace('-', '0').str.strip(), 
                    errors='coerce'
                ).fillna(0).astype(float)

        # 3. 전국 Baseline(평균) 계산
        school_levels = df['학교급'].unique()
        for level in school_levels:
            app.baselines[level] = {}
            level_df = df[df['학교급'] == level]
            
            # 학생수를 숫자로 확실히 변환한 뒤 합산 (에러 발생 지점 방어)
            total_students = float(level_df['학생수'].sum())

            for dim, prefix in app.prefixes.items():
                cols = [c for c in level_df.columns if c.startswith(prefix)]
                
                # 'total_students'가 숫자이므로 이제 에러 없이 비교 가능합니다.
                if total_students > 0:
                    rate_series = (level_df[cols].sum() / total_students) * 1000
                    app.baselines[level][dim] = {k.replace(prefix, '').strip(): v for k, v in rate_series.items()}
                else:
                    app.baselines[level][dim] = {k.replace(prefix, '').strip(): 0 for k in cols}
        
        # 4. 입력 칸 구성을 위한 카테고리 목록 재생성
        for dim, prefix in app.prefixes.items():
            cols = [c for c in df.columns if c.startswith(prefix)]
            app.all_categories[dim] = [c.replace(prefix, '').strip() for c in cols]
            
        return app, df, True
    except Exception as e:
        return app, None, str(e)


# ==========================================
# 3. Streamlit UI (프론트엔드)
# ==========================================
st.title("🧠 스쿨세이프티: 학교 안전 진단 및 솔루션 제공")
st.markdown("""
**[STEP 1] 우리 학교의 사고 통계 파일(장소, 행동, 활동, 형태 등)을 한 번에 업로드하세요.** 엑셀(.xls, .xlsx) 및 CSV를 모두 지원하며, AI가 업로드된 파일을 분석하여 건수를 자동으로 채워줍니다.
""")

# 1) 서버에서 기본 2024 데이터셋 불러오기
app_instance, base_df, load_status = load_data_and_compute_baselines("2024_안전공제회.csv")

if load_status is not True:
    st.error(f"❌ 기본 데이터셋(2024_안전공제회.csv) 불러오기 실패. 백엔드(서버/깃허브)에 파일이 있는지 확인하세요.\n\n에러 메시지: {load_status}")
    st.stop()

# 2) Session State 초기화 (업로드 파일로 자동 채우기 위함)
if 'parsed_counts' not in st.session_state:
    st.session_state.parsed_counts = {dim: {cat: 0 for cat in app_instance.all_categories[dim]} for dim in app_instance.prefixes}

# 3) 파일 업로더 생성
uploaded_files = st.file_uploader("📁 엑셀/CSV 파일 업로드", accept_multiple_files=True, type=['csv', 'xlsx', 'xls'])

if uploaded_files:
    found_count = 0
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith(('.xls', '.xlsx')):
                df_user = pd.read_excel(uploaded_file)
            else:
                # CSV 인코딩 자동 감지 로직
                encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig', 'latin1']
                df_user = None
                for enc in encodings:
                    try:
                        uploaded_file.seek(0)
                        df_user = pd.read_csv(uploaded_file, encoding=enc)
                        break
                    except: continue
                
            if df_user is not None:
                df_user = df_user.fillna('')
                # 데이터 파싱하여 Session state 업데이트
                for dim, categories in app_instance.all_categories.items():
                    for cat in categories:
                        for _, row in df_user.iterrows():
                            if any(cat in str(cell).strip() for cell in row.values):
                               nums = pd.to_numeric(row, errors='coerce').dropna()
                                if len(nums) > 0:
                                    val = int(nums.iloc[-1])
                                    st.session_state.parsed_counts[dim][cat] = val
                                    st.session_state[f"{dim}_{cat}"] = val
                                    found_count += 1
                                break
        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 파일 처리 중 오류가 발생했습니다: {e}")

    if found_count > 0:
        st.success(f"✅ 파싱 완벽 성공! 총 {found_count}개의 항목을 자동 입력했습니다. (아래 탭에서 수정 가능합니다)")


st.divider()
st.markdown("**[STEP 2] 자동 입력된 건수를 확인하고, 학교 정보를 입력한 뒤 분석을 실행하세요.** (수동으로 숫자를 고칠 수도 있습니다)")

col1, col2 = st.columns(2)
with col1:
    my_school_level = st.selectbox("🏫 학교급 선택", ['유치원', '초등학교', '중학교', '고등학교', '특수학교'], index=1)
with col2:
    my_students = st.number_input("👨‍🎓 총 학생 수(명)", min_value=1, value=585)

# 4) 데이터 입력 및 확인용 탭 (Tabs)
st.markdown("### 📊 세부 사고 건수 데이터")
tabs = st.tabs([f"📌 {'활동(시간)' if dim == '활동' else dim}" for dim in app_instance.prefixes.keys()])

for i, dim in enumerate(app_instance.prefixes.keys()):
    with tabs[i]:
        # 4열로 나누어 깔끔하게 배치
        cols = st.columns(4)
        col_idx = 0
        for item in app_instance.all_categories[dim]:
            # Session State의 값을 초기값으로 사용하고, 사용자가 입력하면 다시 Session State 업데이트
            val = cols[col_idx % 4].number_input(
                label=item, 
                min_value=0, 
                value=st.session_state.parsed_counts[dim][item],
                step=1,
                key=f"{dim}_{item}"
            )
            st.session_state.parsed_counts[dim][item] = val
            col_idx += 1


# ==========================================
# 4. 진단 실행 (버튼 클릭 시)
# ==========================================
st.divider()
if st.button("🚀 AI 진단 리포트 실행", type="primary", use_container_width=True):
    
    if my_students <= 0:
        st.error("❌ 학생 수를 정확히 입력해 주세요!")
        st.stop()

    st.header(f"📈 {my_school_level} 맞춤형 4D 큐레이션 진단 리포트")
    st.caption("※ 기준: 학생 1,000명당 발생 건수 환산 비교")

    detected_anomalies = []

    # [차원별 상세 분석] (Expander 사용)
    for dim in app_instance.prefixes.keys():
        display_dim = '활동(시간)' if dim == '활동' else dim
        
        with st.expander(f"📊 [{display_dim}] 차원 상세 분석 펼치기", expanded=False):
            input_counts = st.session_state.parsed_counts[dim]
            total_input = sum(input_counts.values())

            if total_input == 0:
                st.info("입력된 데이터가 없습니다.")
                continue

            # Metric 시각화용 컬럼
            m_cols = st.columns(4)
            m_idx = 0

            for item in app_instance.all_categories[dim]:
                my_count = input_counts.get(item, 0)
                my_rate = (my_count / my_students) * 1000
                avg_rate = app_instance.baselines[my_school_level][dim].get(item, 0)
                diff = my_rate - avg_rate
                ratio = my_rate / avg_rate if avg_rate > 0 else my_rate

                if my_rate >= 0.1 or avg_rate >= 0.1:
                    # Metric으로 깔끔하게 차이 표시 (역방향: diff가 양수면 빨간색/위험)
                    m_cols[m_idx % 4].metric(
                        label=f"{item}", 
                        value=f"우리 {my_rate:.2f}건", 
                        delta=f"{diff:.2f} (전국 {avg_rate:.2f})",
                        delta_color="inverse"
                    )
                    m_idx += 1

                is_anomaly = False
                is_severe = item in app_instance.severe_accidents
                if my_count > 0:
                    if is_severe or (my_count > 1 and my_rate >= (avg_rate * 1.5)):
                        is_anomaly = True

                if is_anomaly:
                    detected_anomalies.append({
                        'dim': dim, 'item': item, 'diff': diff, 'ratio': ratio, 'is_severe': is_severe
                    })

    # [우리학교 최우선 안전교육 Top 5]
    detected_anomalies.sort(key=lambda x: (x['is_severe'], x['ratio']), reverse=True)
    top_5_anomalies = detected_anomalies[:5]

    st.subheader("🏆 [우리학교 최우선 안전교육 Top 5]")
    
    if not top_5_anomalies:
        st.success("✅ 집중 관리해야 할 특이(위험) 항목이 발견되지 않았습니다. 현재의 훌륭한 상태를 유지해 주세요!")
    else:
        for idx, anomaly in enumerate(top_5_anomalies):
            item = anomaly['item']
            ratio_val = anomaly['ratio']
            is_severe = anomaly['is_severe']
            
            if is_severe:
                st.error(f"**{idx+1}위: {item}** \n🚨 **[치명적 사고]** 1건이 발생해도 생명과 직결되는 핵심 위험 항목으로 무관용 원칙에 따라 우선 추출되었습니다.")
            else:
                st.warning(f"**{idx+1}위: {item}** \n📈 **[통계적 이상치]** 전국 동급 학교 평균 발생률 대비 우리 학교의 발생 비율이 **{ratio_val:.1f}배**나 높게 분석되었습니다.")


    # [부서별 역할(R&R) 맞춤형 안전 솔루션]
    if top_5_anomalies:
        st.divider()
        st.subheader("🔥 [부서별 역할(R&R) 맞춤형 안전 솔루션]")
        
        # 학교급 추출 (초등, 중학, 고등)
        level_key = my_school_level[:2]
        if level_key not in ['초등', '중학', '고등']: level_key = '초등'

        # 👨‍🏫 담임 교사 (상단 전체 차지)
        st.info("#### 👨‍🏫 [담임 교사] 맞춤 예방 교육 및 영상 자료")
        for idx, anomaly in enumerate(top_5_anomalies):
            item = anomaly['item']
            sol = app_instance.solutions_db.get(item, app_instance.get_default_solution(item))
            
            vids = []
            if 'videos' in sol:
                vids.extend(sol['videos'].get(level_key, []))
                vids.extend(sol['videos'].get('공통', []))
            if not vids:
                vids.append((f"'{item}' 맞춤형 안전 교육 영상", f"https://www.youtube.com/results?search_query=학교+안전사고+{item}"))

            st.markdown(f"**{idx+1}위 [{item}]**: {sol['담임']}")
            for v_title, v_url in vids:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📺 [{v_title}]({v_url})")

        st.write("") # 간격 띄우기

        # 행정실, 보건실, 안전부장 (3개의 열로 나누어 배치)
        r_cols = st.columns(3)
        
        # 🛠️ 행정실
        with r_cols[0]:
            st.error("#### 🛠️ [행정실] 시설 점검 요청")
            for idx, anomaly in enumerate(top_5_anomalies):
                item = anomaly['item']
                sol = app_instance.solutions_db.get(item, app_instance.get_default_solution(item))
                st.markdown(f"**{idx+1}위: {item}**\n- {sol['행정실']}")

        # 🩹 보건실
        with r_cols[1]:
            st.success("#### 🩹 [보건실] 물품 비축 지침")
            for idx, anomaly in enumerate(top_5_anomalies):
                item = anomaly['item']
                sol = app_instance.solutions_db.get(item, app_instance.get_default_solution(item))
                supplies = next((v for k, v in app_instance.medical_supply_db.items() if k in item), app_instance.medical_supply_db['기타'])
                st.markdown(f"**{idx+1}위: {item}**\n- {sol['보건실']}\n- 💊 **필수 비축:** {supplies}")

        # 📋 안전부장
        with r_cols[2]:
            st.info("#### 📋 [안전부장] 시수 배정 추천")
            top5_names = [f"{i+1}위 {a['item']}" for i, a in enumerate(top_5_anomalies)]
            
            top5_edu_areas = set()
            for a in top_5_anomalies:
                item_name = a['item']
                if any(x in item_name for x in ["교통", "등·하교", "탑승", "스쿨존"]): top5_edu_areas.add("교통안전")
                elif any(x in item_name for x in ["실험", "화학", "열", "전기"]): top5_edu_areas.add("재난안전")
                elif any(x in item_name for x in ["식사", "식중독", "보건", "위생"]): top5_edu_areas.add("보건·위생안전")
                elif any(x in item_name for x in ["싸움", "장난", "폭력"]): top5_edu_areas.add("폭력·신변안전")
                else: top5_edu_areas.add("생활안전")

            safe_pool = ["직업안전", "약물·사이버중독 예방"]
            if "재난안전" not in top5_edu_areas: safe_pool.append("재난안전")
            if "폭력·신변안전" not in top5_edu_areas: safe_pool.append("폭력·신변안전")
            
            st.markdown(f"**📊 데이터 근거:**\n가장 위험한 사고(1위) 발생률이 전국 평균 대비 **{top_5_anomalies[0]['ratio']:.1f}배** 높습니다.")
            st.markdown(f"**👉 [51시간 시수 교환 방안]**\n의무 51시간 중 자율 편성권을 활용하여 안정권인 **[{', '.join(safe_pool)}]** 에서 시수를 줄이고, 위험이 폭증한 **[{', '.join(top5_names)}]** 에 집중 편성하십시오.")