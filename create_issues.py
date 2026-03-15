#!/usr/bin/env python3
"""Issue 10개 생성 스크립트 (현재 토큰으로 실행 가능)"""
import requests, json, time, sys, yaml
from datetime import datetime, timedelta

OWNER = "vibrissa83"
REPO  = "drivers_high"
REST  = "https://api.github.com"
TODAY = datetime.today()

def d(offset): return (TODAY + timedelta(days=offset)).strftime("%Y-%m-%d")

ISSUES = [
    {
        "title": "[UI] 좌측 패널에 속도 표시 추가 (점수 아래)",
        "labels": ["ui", "feature"],
        "priority": "P0", "start": d(0), "end": d(3),
        "body": """## 개요
상단 좌측 HUD 패널에 현재 속도를 점수 아래에 표시한다.

## Definition of Done
- [ ] `#topLeft` 패널에 `속도: XXX` 라인 추가
- [ ] 부스터 레벨에 따라 속도 색상이 변경됨 (일반=흰, Lv1=초록, Lv2=주황, Lv3=빨강)
- [ ] 모바일(375px 이하)에서 레이아웃 깨짐 없이 표시 확인
- [ ] 기존 점수·거리 표시와 세로 간격 일정 유지

**Priority**: P0 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Scale] 도로/차량 스케일 리밸런싱 (차량이 도로 폭의 2/3 체감)",
        "labels": ["balance", "ui"],
        "priority": "P0", "start": d(0), "end": d(3),
        "body": """## 개요
현재 차량이 차선 대비 너무 작거나 커서 밸런스 조정이 필요하다.

## Definition of Done
- [ ] 플레이어 차량 너비를 차선 폭의 약 60~65%로 조정
- [ ] 장애물 차량도 동일 비율 적용
- [ ] 3차선 모두에서 차량이 자연스럽게 주행하는지 시각 확인
- [ ] 충돌 히트박스도 시각 크기에 맞춰 재조정

**Priority**: P0 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Road] 도로 '깊이감' 연출 강화 (시야/스크롤)",
        "labels": ["ui", "feature"],
        "priority": "P1", "start": d(2), "end": d(6),
        "body": """## 개요
현재 도로가 평면적으로 보임. 원근감·깊이감을 강화한다.

## Definition of Done
- [ ] 차선 대시 스크롤 속도가 player.speed에 비례해 변함
- [ ] 도로 양 끝에 그라디언트 또는 그림자 처리 추가
- [ ] 속도 증가 시 차선 간격이 시각적으로 빨라 보이는 효과 구현
- [ ] 잔디 영역에 속도감 줄무늬 또는 패럴랙스 효과 추가

**Priority**: P1 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Booster] 2단계 밀치기 물리 개선 (측면 넉백/속도 페널티)",
        "labels": ["balance", "feature"],
        "priority": "P1", "start": d(2), "end": d(7),
        "body": """## 개요
2단계 부스터의 밀치기(push) 동작이 너무 단순함. 물리적으로 자연스럽게 개선한다.

## Definition of Done
- [ ] 밀쳐진 장애물이 측면으로 서서히 가속되며 화면 밖으로 나감
- [ ] 밀치기 발생 시 장애물에 회전 효과(기울기) 적용
- [ ] 장애물이 도로 밖으로 나가면 잔디 영역에서 추가 감속
- [ ] 밀치기 시 짧은 충격 이펙트(플래시/진동) 표시

**Priority**: P1 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Booster] 3단계 파괴 이펙트 (파티클/플로팅 텍스트)",
        "labels": ["feature", "ui"],
        "priority": "P1", "start": d(3), "end": d(8),
        "body": """## 개요
3단계 부스터로 장애물 파괴 시 시각 효과가 빈약함. 파티클 및 플로팅 텍스트를 강화한다.

## Definition of Done
- [ ] 파괴 시 최소 8개 이상의 파티클이 방사형으로 퍼짐
- [ ] 파티클은 중력(아래 가속도)과 페이드아웃 적용
- [ ] `💥 +50` 플로팅 텍스트가 1초간 위로 떠오르다 사라짐
- [ ] 화면 전체 0.1초 짧은 플래시(flash) 이펙트 추가
- [ ] 파티클 색상이 장애물 차량 색상을 반영

**Priority**: P1 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Balance] 난이도 램프 튜닝 (15초마다 증가 값 검증)",
        "labels": ["balance"],
        "priority": "P1", "start": d(4), "end": d(9),
        "body": """## 개요
15초 주기 난이도 증가값(diffRampAmount=0.15)의 적정성을 검증하고 조정한다.

## Definition of Done
- [ ] 1분 플레이 기준 장애물 속도 변화 로그 기록 및 분석
- [ ] 체감 난이도 곡선이 30초~2분 구간에서 적절한지 5회 이상 테스트
- [ ] 필요 시 rampAmount 또는 rampInterval 값 조정 및 상수화(CFG에 명시)
- [ ] 최대 난이도 cap(상한선) 설정 확인

**Priority**: P1 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[UX] 시작 화면에 간단 튜토리얼 (드래그 안내)",
        "labels": ["ui", "feature"],
        "priority": "P2", "start": d(5), "end": d(10),
        "body": """## 개요
첫 플레이 사용자를 위해 시작 화면에 드래그 조작 튜토리얼을 추가한다.

## Definition of Done
- [ ] 시작 화면에 손가락 아이콘 + 좌우 화살표 애니메이션 표시
- [ ] `첫 플레이` 여부를 localStorage로 감지, 이미 플레이했으면 스킵
- [ ] 게임 중 처음 3초간 반투명 드래그 힌트 오버레이 표시
- [ ] 힌트는 터치 시작 시 즉시 사라짐

**Priority**: P2 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Tech] 로컬 최고점수 (LocalStorage) 표시/초기화 UX 점검",
        "labels": ["tech-debt", "ui"],
        "priority": "P2", "start": d(5), "end": d(10),
        "body": """## 개요
LocalStorage 기반 최고 점수 저장의 UX를 점검하고 초기화 기능을 추가한다.

## Definition of Done
- [ ] 시작 화면에 현재 최고 점수가 올바르게 표시됨 확인
- [ ] 게임 오버 화면에서 신기록 갱신 시 애니메이션(🏆 배지) 정상 동작 확인
- [ ] 설정 또는 게임 오버 화면에 '기록 초기화' 버튼 추가
- [ ] 초기화 시 confirm 다이얼로그로 실수 방지

**Priority**: P2 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Docs] README에 조작/규칙/로드맵 링크 업데이트",
        "labels": ["docs"],
        "priority": "P2", "start": d(8), "end": d(12),
        "body": """## 개요
README.md를 최신 게임 상태에 맞게 업데이트하고 GitHub Project 로드맵 링크를 추가한다.

## Definition of Done
- [ ] 조작법 섹션이 현재 상대 드래그 방식으로 정확히 기술됨
- [ ] 부스터 시스템 표(레벨/효과/색상) 최신화
- [ ] GitHub Project URL 링크가 README에 포함됨
- [ ] 배포된 GitHub Pages URL이 명시됨 (있는 경우)

**Priority**: P2 | **Start**: {start} | **End**: {end}
""",
    },
    {
        "title": "[Release] GitHub Pages 배포 설정 및 URL 정리",
        "labels": ["tech-debt", "docs"],
        "priority": "P2", "start": d(10), "end": d(14),
        "body": """## 개요
main 브랜치 기준으로 GitHub Pages 배포를 설정하고 공개 URL을 확보한다.

## Definition of Done
- [ ] Repository Settings > Pages에서 `main` 브랜치 `/` (root) 배포 설정 완료
- [ ] `https://vibrissa83.github.io/drivers_high/` 에서 게임이 정상 로딩됨
- [ ] README에 배포 URL 배지(badge) 추가
- [ ] 모바일 Chrome / Safari에서 배포 URL 접속 및 플레이 확인

**Priority**: P2 | **Start**: {start} | **End**: {end}
""",
    },
]

def get_token():
    with open('/home/user/.config/gh/hosts.yml') as f:
        data = yaml.safe_load(f)
    return data.get('github.com', {}).get('oauth_token', '')

def create_issue(token, title, body, labels):
    body_filled = body.format(start="(날짜 설정됨)", end="(날짜 설정됨)")
    r = requests.post(
        f"{REST}/repos/{OWNER}/{REPO}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"title": title, "body": body_filled, "labels": labels}
    )
    r.raise_for_status()
    return r.json()

def main():
    token = get_token()
    print("🚀 Issue 10개 생성 시작...")
    results = []
    for i, issue in enumerate(ISSUES, 1):
        result = create_issue(token, issue["title"], issue["body"], issue["labels"])
        num = result["number"]
        url = result["html_url"]
        results.append({"number": num, "url": url, "node_id": result["node_id"],
                        "title": issue["title"], "priority": issue["priority"],
                        "start": issue["start"], "end": issue["end"]})
        print(f"  [{i:02d}/10] #{num} {issue['title'][:55]}...")
        time.sleep(0.4)
    
    with open("/home/user/webapp/issues_result.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 완료! issues_result.json 저장됨")
    print(f"📋 Issues: https://github.com/{OWNER}/{REPO}/issues")
    return results

if __name__ == "__main__":
    main()
