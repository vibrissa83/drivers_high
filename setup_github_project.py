#!/usr/bin/env python3
"""
GitHub Project v2 + Issues + Labels 전체 셋업 스크립트
Usage:
    python3 setup_github_project.py --token <PAT_WITH_PROJECT_SCOPE>
    또는 환경변수: GH_PAT=<token> python3 setup_github_project.py
"""

import requests
import json
import sys
import os
import time
import argparse
from datetime import datetime, timedelta

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
OWNER      = "vibrissa83"
REPO       = "drivers_high"
REPO_ID    = "R_kgDORkuKJw"       # REST node_id
OWNER_ID   = "U_kgDOCcNhSQ"       # User node_id

PROJECT_TITLE = "drivers_high - Task / Backlog / Roadmap"
PROJECT_DESC  = "모바일 레이싱 웹게임 MVP의 할일/백로그/로드맵 관리"

TODAY     = datetime.today()
MVP_START = TODAY.strftime("%Y-%m-%d")
MVP_END   = (TODAY + timedelta(days=14)).strftime("%Y-%m-%d")

GRAPHQL_URL = "https://api.github.com/graphql"
REST_BASE   = "https://api.github.com"

# ─────────────────────────────────────────
#  LABELS
# ─────────────────────────────────────────
LABELS = [
    {"name": "feature",    "color": "0075ca", "description": "새 기능"},
    {"name": "ui",         "color": "e4e669", "description": "UI/UX 관련"},
    {"name": "balance",    "color": "d93f0b", "description": "게임 밸런스"},
    {"name": "tech-debt",  "color": "5319e7", "description": "기술 부채"},
    {"name": "docs",       "color": "0e8a16", "description": "문서화"},
]

# ─────────────────────────────────────────
#  ISSUES  (title, labels, priority, body, start, end)
# ─────────────────────────────────────────
def d(offset): return (TODAY + timedelta(days=offset)).strftime("%Y-%m-%d")

ISSUES = [
    {
        "title": "[UI] 좌측 패널에 속도 표시 추가 (점수 아래)",
        "labels": ["ui", "feature"],
        "priority": "P0",
        "start": d(0), "end": d(3),
        "body": """## 개요
상단 좌측 HUD 패널에 현재 속도를 점수 아래에 표시한다.

## Definition of Done
- [ ] `#topLeft` 패널에 `속도: XXX` 라인 추가
- [ ] 부스터 레벨에 따라 속도 색상이 변경됨 (일반=흰, Lv1=초록, Lv2=주황, Lv3=빨강)
- [ ] 모바일(375px 이하)에서 레이아웃 깨짐 없이 표시 확인
- [ ] 기존 점수·거리 표시와 세로 간격 일정 유지
"""
    },
    {
        "title": "[Scale] 도로/차량 스케일 리밸런싱 (차량이 도로 폭의 2/3 체감)",
        "labels": ["balance", "ui"],
        "priority": "P0",
        "start": d(0), "end": d(3),
        "body": """## 개요
현재 차량이 차선 대비 너무 작거나 커서 밸런스 조정이 필요하다.

## Definition of Done
- [ ] 플레이어 차량 너비를 차선 폭의 약 60~65%로 조정
- [ ] 장애물 차량도 동일 비율 적용
- [ ] 3차선 모두에서 차량이 자연스럽게 주행하는지 시각 확인
- [ ] 충돌 히트박스도 시각 크기에 맞춰 재조정
"""
    },
    {
        "title": "[Road] 도로 '깊이감' 연출 강화 (시야/스크롤)",
        "labels": ["ui", "feature"],
        "priority": "P1",
        "start": d(2), "end": d(6),
        "body": """## 개요
현재 도로가 평면적으로 보임. 원근감·깊이감을 강화한다.

## Definition of Done
- [ ] 차선 대시 스크롤 속도가 player.speed에 비례해 변함
- [ ] 도로 양 끝에 그라디언트 또는 그림자 처리 추가
- [ ] 속도 증가 시 차선 간격이 시각적으로 빨라 보이는 효과 구현
- [ ] 잔디 영역에 속도감 줄무늬 또는 패럴랙스 효과 추가
"""
    },
    {
        "title": "[Booster] 2단계 밀치기 물리 개선 (측면 넉백/속도 페널티)",
        "labels": ["balance", "feature"],
        "priority": "P1",
        "start": d(2), "end": d(7),
        "body": """## 개요
2단계 부스터의 밀치기(push) 동작이 너무 단순함. 물리적으로 자연스럽게 개선한다.

## Definition of Done
- [ ] 밀쳐진 장애물이 측면으로 서서히 가속되며 화면 밖으로 나감
- [ ] 밀치기 발생 시 장애물에 회전 효과(기울기) 적용
- [ ] 장애물이 도로 밖으로 나가면 잔디 영역에서 추가 감속
- [ ] 밀치기 시 짧은 충격 이펙트(플래시/진동) 표시
"""
    },
    {
        "title": "[Booster] 3단계 파괴 이펙트 (파티클/플로팅 텍스트)",
        "labels": ["feature", "ui"],
        "priority": "P1",
        "start": d(3), "end": d(8),
        "body": """## 개요
3단계 부스터로 장애물 파괴 시 시각 효과가 빈약함. 파티클 및 플로팅 텍스트를 강화한다.

## Definition of Done
- [ ] 파괴 시 최소 8개 이상의 파티클이 방사형으로 퍼짐
- [ ] 파티클은 중력(아래 가속도)과 페이드아웃 적용
- [ ] `💥 +50` 플로팅 텍스트가 1초간 위로 떠오르다 사라짐
- [ ] 화면 전체 0.1초 짧은 플래시(flash) 이펙트 추가
- [ ] 파티클 색상이 장애물 차량 색상을 반영
"""
    },
    {
        "title": "[Balance] 난이도 램프 튜닝 (15초마다 증가 값 검증)",
        "labels": ["balance"],
        "priority": "P1",
        "start": d(4), "end": d(9),
        "body": """## 개요
15초 주기 난이도 증가값(diffRampAmount=0.15)의 적정성을 검증하고 조정한다.

## Definition of Done
- [ ] 1분 플레이 기준 장애물 속도 변화 로그 기록 및 분석
- [ ] 체감 난이도 곡선이 30초~2분 구간에서 적절한지 5회 이상 테스트
- [ ] 필요 시 rampAmount 또는 rampInterval 값 조정 및 상수화(CFG에 명시)
- [ ] 최대 난이도 cap(상한선) 설정 확인
"""
    },
    {
        "title": "[UX] 시작 화면에 간단 튜토리얼 (드래그 안내)",
        "labels": ["ui", "feature"],
        "priority": "P2",
        "start": d(5), "end": d(10),
        "body": """## 개요
첫 플레이 사용자를 위해 시작 화면에 드래그 조작 튜토리얼을 추가한다.

## Definition of Done
- [ ] 시작 화면에 손가락 아이콘 + 좌우 화살표 애니메이션 표시
- [ ] `첫 플레이` 여부를 localStorage로 감지, 이미 플레이했으면 스킵
- [ ] 게임 중 처음 3초간 반투명 드래그 힌트 오버레이 표시
- [ ] 힌트는 터치 시작 시 즉시 사라짐
"""
    },
    {
        "title": "[Tech] 로컬 최고점수 (LocalStorage) 표시/초기화 UX 점검",
        "labels": ["tech-debt", "ui"],
        "priority": "P2",
        "start": d(5), "end": d(10),
        "body": """## 개요
LocalStorage 기반 최고 점수 저장의 UX를 점검하고 초기화 기능을 추가한다.

## Definition of Done
- [ ] 시작 화면에 현재 최고 점수가 올바르게 표시됨 확인
- [ ] 게임 오버 화면에서 신기록 갱신 시 애니메이션(🏆 배지) 정상 동작 확인
- [ ] 설정 또는 게임 오버 화면에 '기록 초기화' 버튼 추가
- [ ] 초기화 시 confirm 다이얼로그로 실수 방지
"""
    },
    {
        "title": "[Docs] README에 조작/규칙/로드맵 링크 업데이트",
        "labels": ["docs"],
        "priority": "P2",
        "start": d(8), "end": d(12),
        "body": """## 개요
README.md를 최신 게임 상태에 맞게 업데이트하고 GitHub Project 로드맵 링크를 추가한다.

## Definition of Done
- [ ] 조작법 섹션이 현재 상대 드래그 방식으로 정확히 기술됨
- [ ] 부스터 시스템 표(레벨/효과/색상) 최신화
- [ ] GitHub Project URL 링크가 README에 포함됨
- [ ] 배포된 GitHub Pages URL이 명시됨 (있는 경우)
"""
    },
    {
        "title": "[Release] GitHub Pages 배포 설정 및 URL 정리",
        "labels": ["tech-debt", "docs"],
        "priority": "P2",
        "start": d(10), "end": d(14),
        "body": """## 개요
main 브랜치 기준으로 GitHub Pages 배포를 설정하고 공개 URL을 확보한다.

## Definition of Done
- [ ] Repository Settings > Pages에서 `main` 브랜치 `/` (root) 배포 설정 완료
- [ ] `https://vibrissa83.github.io/drivers_high/` 에서 게임이 정상 로딩됨
- [ ] README에 배포 URL 배지(badge) 추가
- [ ] 모바일 Chrome / Safari에서 배포 URL 접속 및 플레이 확인
"""
    },
]


# ─────────────────────────────────────────
#  HTTP HELPERS
# ─────────────────────────────────────────
def gql(token, query, variables=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Github-Next-Global-ID": "1",
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(GRAPHQL_URL, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL Error: {json.dumps(data['errors'], indent=2)}")
    return data["data"]

def rest(token, method, path, body=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"{REST_BASE}{path}"
    r = getattr(requests, method)(url, headers=headers, json=body)
    if r.status_code == 422:
        return r.json()   # 이미 존재하는 경우 등
    r.raise_for_status()
    return r.json() if r.text else {}


# ─────────────────────────────────────────
#  STEP 1: PROJECT 생성
# ─────────────────────────────────────────
def create_project(token):
    print("\n[1/6] 🏗  GitHub Project v2 생성 중...")
    q = """
    mutation CreateProject($ownerId: ID!, $title: String!) {
      createProjectV2(input: { ownerId: $ownerId, title: $title }) {
        projectV2 { id number url title }
      }
    }"""
    data = gql(token, q, {"ownerId": OWNER_ID, "title": PROJECT_TITLE})
    proj = data["createProjectV2"]["projectV2"]
    print(f"  ✅ 생성됨: {proj['url']}")
    return proj


# ─────────────────────────────────────────
#  STEP 2: PROJECT DESCRIPTION 업데이트
# ─────────────────────────────────────────
def update_project_desc(token, project_id):
    print("[2/6] 📝  프로젝트 설명 업데이트...")
    q = """
    mutation UpdateProject($id: ID!, $desc: String!) {
      updateProjectV2(input: { projectId: $id, shortDescription: $desc }) {
        projectV2 { id }
      }
    }"""
    gql(token, q, {"id": project_id, "desc": PROJECT_DESC})
    print("  ✅ 설명 업데이트 완료")


# ─────────────────────────────────────────
#  STEP 3: 필드 구성
# ─────────────────────────────────────────
def get_existing_fields(token, project_id):
    q = """
    query GetFields($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field { id name dataType }
              ... on ProjectV2SingleSelectField { id name dataType options { id name } }
              ... on ProjectV2IterationField { id name dataType }
            }
          }
        }
      }
    }"""
    data = gql(token, q, {"id": project_id})
    return data["node"]["fields"]["nodes"]


def setup_fields(token, project_id):
    print("[3/6] 🔧  필드 구성 중...")
    fields = get_existing_fields(token, project_id)
    field_map = {}
    for f in fields:
        if f.get("name"):
            field_map[f["name"]] = f

    # Status 필드 (기본 존재)
    status_field = field_map.get("Status")
    if status_field:
        print(f"  ✅ Status 필드 존재: {status_field['id']}")
        # Status 옵션 확인 및 필요 시 추가
        existing_opts = {o["name"] for o in status_field.get("options", [])}
        print(f"     현재 옵션: {existing_opts}")
    
    # Priority 단일선택 필드 생성
    if "Priority" not in field_map:
        q = """
        mutation AddSingleSelect($projectId: ID!, $name: String!, $opts: [ProjectV2SingleSelectFieldOptionInput!]!) {
          createProjectV2Field(input: {
            projectId: $projectId,
            dataType: SINGLE_SELECT,
            name: $name,
            singleSelectOptions: $opts
          }) {
            projectV2Field {
              ... on ProjectV2SingleSelectField { id name options { id name } }
            }
          }
        }"""
        opts = [
            {"name": "P0", "color": "RED",    "description": "Critical"},
            {"name": "P1", "color": "ORANGE", "description": "High"},
            {"name": "P2", "color": "YELLOW", "description": "Normal"},
        ]
        data = gql(token, q, {"projectId": project_id, "name": "Priority", "opts": opts})
        pf = data["createProjectV2Field"]["projectV2Field"]
        field_map["Priority"] = pf
        print(f"  ✅ Priority 필드 생성: {pf['id']}")
    else:
        print(f"  ✅ Priority 필드 이미 존재")

    # Start date 필드
    if "Start date" not in field_map:
        q = """
        mutation AddDate($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {
            projectId: $projectId, dataType: DATE, name: $name
          }) {
            projectV2Field {
              ... on ProjectV2Field { id name }
            }
          }
        }"""
        data = gql(token, q, {"projectId": project_id, "name": "Start date"})
        sf = data["createProjectV2Field"]["projectV2Field"]
        field_map["Start date"] = sf
        print(f"  ✅ Start date 필드 생성: {sf['id']}")
    else:
        print(f"  ✅ Start date 필드 이미 존재")

    # End date 필드
    if "End date" not in field_map:
        q = """
        mutation AddDate($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {
            projectId: $projectId, dataType: DATE, name: $name
          }) {
            projectV2Field {
              ... on ProjectV2Field { id name }
            }
          }
        }"""
        data = gql(token, q, {"projectId": project_id, "name": "End date"})
        ef = data["createProjectV2Field"]["projectV2Field"]
        field_map["End date"] = ef
        print(f"  ✅ End date 필드 생성: {ef['id']}")
    else:
        print(f"  ✅ End date 필드 이미 존재")

    return field_map


# ─────────────────────────────────────────
#  STEP 4: VIEW 3개 생성
# ─────────────────────────────────────────
def setup_views(token, project_id):
    print("[4/6] 👁  View 3개 생성 중...")
    # View 생성 mutation
    q = """
    mutation CreateView($projectId: ID!, $name: String!, $layout: ProjectV2ViewLayout!) {
      createProjectV2View(input: {
        projectId: $projectId,
        name: $name,
        layout: $layout
      }) {
        projectV2View { id name layout }
      }
    }"""
    
    views = {}
    
    # View A: Backlog (TABLE)
    try:
        data = gql(token, q, {"projectId": project_id, "name": "📋 Backlog", "layout": "TABLE_LAYOUT"})
        v = data["createProjectV2View"]["projectV2View"]
        views["backlog"] = v
        print(f"  ✅ Backlog (Table) view 생성: {v['id']}")
    except Exception as e:
        print(f"  ⚠️  Backlog view 생성 실패: {e}")

    # View B: Kanban (BOARD)
    try:
        data = gql(token, q, {"projectId": project_id, "name": "🗂 Kanban", "layout": "BOARD_LAYOUT"})
        v = data["createProjectV2View"]["projectV2View"]
        views["kanban"] = v
        print(f"  ✅ Kanban (Board) view 생성: {v['id']}")
    except Exception as e:
        print(f"  ⚠️  Kanban view 생성 실패: {e}")

    # View C: Roadmap
    try:
        data = gql(token, q, {"projectId": project_id, "name": "🗓 Roadmap", "layout": "ROADMAP_LAYOUT"})
        v = data["createProjectV2View"]["projectV2View"]
        views["roadmap"] = v
        print(f"  ✅ Roadmap (Timeline) view 생성: {v['id']}")
    except Exception as e:
        # ROADMAP_LAYOUT이 안되면 TABLE로 폴백
        print(f"  ⚠️  Roadmap layout 불가, Table로 대체: {e}")
        try:
            data = gql(token, q, {"projectId": project_id, "name": "🗓 Roadmap", "layout": "TABLE_LAYOUT"})
            v = data["createProjectV2View"]["projectV2View"]
            views["roadmap"] = v
        except:
            pass

    return views


# ─────────────────────────────────────────
#  STEP 5: LABELS 생성
# ─────────────────────────────────────────
def create_labels(token):
    print("[5/6] 🏷  라벨 생성 중...")
    label_map = {}
    for label in LABELS:
        result = rest(token, "post",
                      f"/repos/{OWNER}/{REPO}/labels",
                      {"name": label["name"], "color": label["color"],
                       "description": label["description"]})
        if "id" in result:
            print(f"  ✅ 라벨 생성: {label['name']}")
        else:
            # 이미 존재하면 조회
            existing = rest(token, "get", f"/repos/{OWNER}/{REPO}/labels/{label['name']}")
            print(f"  ℹ️  라벨 이미 존재: {label['name']}")
        label_map[label["name"]] = label["name"]
    return label_map


# ─────────────────────────────────────────
#  STEP 6: ISSUES 생성 + PROJECT 연결 + 필드 값 설정
# ─────────────────────────────────────────
def get_issue_node_id(token, issue_number):
    q = """
    query GetIssue($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) { id }
      }
    }"""
    data = gql(token, q, {"owner": OWNER, "repo": REPO, "number": issue_number})
    return data["repository"]["issue"]["id"]


def add_issue_to_project(token, project_id, issue_node_id):
    q = """
    mutation AddItem($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) {
        item { id }
      }
    }"""
    data = gql(token, q, {"projectId": project_id, "contentId": issue_node_id})
    return data["addProjectV2ItemById"]["item"]["id"]


def set_field_value(token, project_id, item_id, field_id, value_dict):
    q = """
    mutation SetField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: $value
      }) {
        projectV2Item { id }
      }
    }"""
    gql(token, q, {
        "projectId": project_id,
        "itemId":    item_id,
        "fieldId":   field_id,
        "value":     value_dict,
    })


def create_issues(token, project_id, field_map):
    print("[6/6] 📌  Issue 10개 생성 + Project 연결 중...")

    # 필드 ID 수집
    fields_fresh = get_existing_fields(token, project_id)
    fid = {}
    for f in fields_fresh:
        name = f.get("name", "")
        fid[name] = f

    status_field   = fid.get("Status")
    priority_field = fid.get("Priority")
    start_field    = fid.get("Start date")
    end_field      = fid.get("End date")

    # Status 옵션 ID 수집
    status_opts = {}
    if status_field and "options" in status_field:
        for opt in status_field["options"]:
            status_opts[opt["name"]] = opt["id"]
    print(f"  Status 옵션: {list(status_opts.keys())}")

    priority_opts = {}
    if priority_field and "options" in priority_field:
        for opt in priority_field["options"]:
            priority_opts[opt["name"]] = opt["id"]
    print(f"  Priority 옵션: {list(priority_opts.keys())}")

    issue_urls = []

    for idx, issue in enumerate(ISSUES, 1):
        # 이슈 생성
        result = rest(token, "post",
                      f"/repos/{OWNER}/{REPO}/issues",
                      {
                          "title":  issue["title"],
                          "body":   issue["body"],
                          "labels": issue["labels"],
                      })
        issue_number = result["number"]
        issue_url    = result["html_url"]
        issue_urls.append(issue_url)
        print(f"  ✅ Issue #{issue_number}: {issue['title'][:50]}...")

        # node_id 가져오기
        issue_node_id = get_issue_node_id(token, issue_number)

        # Project에 추가
        item_id = add_issue_to_project(token, project_id, issue_node_id)

        # Status = Backlog 설정
        backlog_id = status_opts.get("Backlog") or status_opts.get("Todo") or (list(status_opts.values())[0] if status_opts else None)
        if backlog_id and status_field:
            try:
                set_field_value(token, project_id, item_id,
                                status_field["id"],
                                {"singleSelectOptionId": backlog_id})
            except Exception as e:
                print(f"     ⚠️  Status 설정 실패: {e}")

        # Priority 설정
        p_key = issue["priority"]
        p_id  = priority_opts.get(p_key)
        if p_id and priority_field:
            try:
                set_field_value(token, project_id, item_id,
                                priority_field["id"],
                                {"singleSelectOptionId": p_id})
            except Exception as e:
                print(f"     ⚠️  Priority 설정 실패: {e}")

        # Start date 설정
        if start_field:
            try:
                set_field_value(token, project_id, item_id,
                                start_field["id"],
                                {"date": issue["start"]})
            except Exception as e:
                print(f"     ⚠️  Start date 설정 실패: {e}")

        # End date 설정
        if end_field:
            try:
                set_field_value(token, project_id, item_id,
                                end_field["id"],
                                {"date": issue["end"]})
            except Exception as e:
                print(f"     ⚠️  End date 설정 실패: {e}")

        time.sleep(0.3)  # rate limit 방지

    return issue_urls


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get("GH_PAT", ""))
    args = parser.parse_args()

    token = args.token.strip()
    if not token:
        print("❌ 토큰이 없습니다. --token <PAT> 또는 GH_PAT 환경변수를 설정해주세요.")
        sys.exit(1)

    print("=" * 55)
    print("🏎️  drivers_high GitHub Project 셋업 시작")
    print("=" * 55)

    try:
        # 1. 프로젝트 생성
        proj = create_project(token)
        project_id  = proj["id"]
        project_url = proj["url"]

        # 2. 설명 업데이트
        update_project_desc(token, project_id)

        # 3. 필드 구성
        field_map = setup_fields(token, project_id)

        # 4. View 생성
        views = setup_views(token, project_id)

        # 5. 라벨 생성
        create_labels(token)

        # 6. Issue 생성 + 연결
        issue_urls = create_issues(token, project_id, field_map)

        print("\n" + "=" * 55)
        print("✅  모든 작업 완료!")
        print("=" * 55)
        print(f"\n🔗 Project URL:\n   {project_url}")
        print(f"\n📋 Issues 목록:\n   https://github.com/{OWNER}/{REPO}/issues")
        print(f"\n📌 생성된 Issue URL:")
        for url in issue_urls:
            print(f"   {url}")

        # 결과 저장
        result = {
            "project_url": project_url,
            "project_id": project_id,
            "issues_url": f"https://github.com/{OWNER}/{REPO}/issues",
            "issue_urls": issue_urls,
        }
        with open("/home/user/webapp/project_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 결과가 project_result.json에 저장되었습니다.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
