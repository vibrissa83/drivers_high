#!/usr/bin/env python3
"""
GitHub Project v2 생성 + Issue 연결 스크립트
PAT(Personal Access Token) 필요: project, repo 권한

사용법:
  GH_PAT=ghp_xxxx python3 create_project_with_pat.py
  또는
  python3 create_project_with_pat.py --token ghp_xxxx
"""
import requests, json, time, sys, os, argparse, yaml
from datetime import datetime, timedelta

OWNER    = "vibrissa83"
REPO     = "drivers_high"
OWNER_ID = "U_kgDOCcNhSQ"
GQL_URL  = "https://api.github.com/graphql"
REST     = "https://api.github.com"

def gql(token, query, variables=None):
    r = requests.post(GQL_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"query": query, "variables": variables or {}})
    r.raise_for_status()
    d = r.json()
    if "errors" in d:
        raise RuntimeError(json.dumps(d["errors"], indent=2))
    return d["data"]

def rest_call(token, method, path, body=None):
    r = getattr(requests, method)(
        f"{REST}{path}",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"},
        json=body)
    if r.status_code in (200, 201): return r.json()
    if r.status_code == 204: return {}
    if r.status_code == 422: return r.json()  # already exists
    r.raise_for_status()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get("GH_PAT",""))
    args = parser.parse_args()
    token = args.token.strip()
    if not token:
        print("❌ --token 또는 GH_PAT 환경변수 필요")
        print("\n📌 PAT 발급 방법:")
        print("  1. https://github.com/settings/tokens/new 접속")
        print("  2. 이름: drivers_high-project-setup")
        print("  3. 권한 체크: repo (전체) + project (전체)")
        print("  4. Generate token 클릭")
        print("  5. GH_PAT=ghp_xxxx python3 create_project_with_pat.py")
        sys.exit(1)

    print("=" * 55)
    print("🏎️  GitHub Project v2 생성 시작")
    print("=" * 55)

    # ── 1. Project 생성 ──
    print("\n[1] Project 생성...")
    d = gql(token, """
      mutation($ownerId: ID!, $title: String!) {
        createProjectV2(input: { ownerId: $ownerId, title: $title }) {
          projectV2 { id number url title }
        }
      }""", {"ownerId": OWNER_ID, "title": "drivers_high - Task / Backlog / Roadmap"})
    proj = d["createProjectV2"]["projectV2"]
    pid, purl = proj["id"], proj["url"]
    print(f"  ✅ {purl}")

    # ── 2. 설명 업데이트 ──
    gql(token, """
      mutation($id: ID!, $desc: String!) {
        updateProjectV2(input: { projectId: $id, shortDescription: $desc }) {
          projectV2 { id }
        }
      }""", {"id": pid, "desc": "모바일 레이싱 웹게임 MVP의 할일/백로그/로드맵 관리"})
    print("[2] ✅ 프로젝트 설명 업데이트")

    # ── 3. Priority 필드 생성 ──
    print("[3] 필드 생성...")
    fd = gql(token, """
      mutation($pid: ID!) {
        createProjectV2Field(input: {
          projectId: $pid, dataType: SINGLE_SELECT, name: "Priority",
          singleSelectOptions: [
            {name: "P0", color: RED,    description: "Critical"},
            {name: "P1", color: ORANGE, description: "High"},
            {name: "P2", color: YELLOW, description: "Normal"}
          ]
        }) {
          projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name } } }
        }
      }""", {"pid": pid})
    pf = fd["createProjectV2Field"]["projectV2Field"]
    priority_opts = {o["name"]: o["id"] for o in pf["options"]}
    print(f"  ✅ Priority 필드: {pf['id']}")

    # Start date
    sd = gql(token, """
      mutation($pid: ID!) {
        createProjectV2Field(input: { projectId: $pid, dataType: DATE, name: "Start date" }) {
          projectV2Field { ... on ProjectV2Field { id name } }
        }
      }""", {"pid": pid})
    start_fid = sd["createProjectV2Field"]["projectV2Field"]["id"]
    print(f"  ✅ Start date 필드: {start_fid}")

    # End date
    ed = gql(token, """
      mutation($pid: ID!) {
        createProjectV2Field(input: { projectId: $pid, dataType: DATE, name: "End date" }) {
          projectV2Field { ... on ProjectV2Field { id name } }
        }
      }""", {"pid": pid})
    end_fid = ed["createProjectV2Field"]["projectV2Field"]["id"]
    print(f"  ✅ End date 필드: {end_fid}")

    # ── 4. Status 필드 ID + Backlog 옵션 ID ──
    fq = gql(token, """
      query($id: ID!) {
        node(id: $id) {
          ... on ProjectV2 {
            fields(first: 20) {
              nodes {
                ... on ProjectV2SingleSelectField { id name options { id name } }
                ... on ProjectV2Field { id name dataType }
              }
            }
          }
        }
      }""", {"id": pid})
    all_fields = fq["node"]["fields"]["nodes"]
    status_field = next((f for f in all_fields if f.get("name") == "Status"), None)
    status_fid   = status_field["id"]
    status_opts  = {o["name"]: o["id"] for o in status_field.get("options", [])}
    backlog_oid  = (status_opts.get("Backlog") or status_opts.get("Todo")
                    or list(status_opts.values())[0])
    print(f"  ✅ Status 필드: {status_fid} | Backlog옵션: {backlog_oid}")

    # ── 5. Views ──
    print("[4] View 생성...")
    for name, layout in [("📋 Backlog","TABLE_LAYOUT"),("🗂 Kanban","BOARD_LAYOUT"),("🗓 Roadmap","ROADMAP_LAYOUT")]:
        try:
            gql(token, """
              mutation($pid: ID!, $name: String!, $layout: ProjectV2ViewLayout!) {
                createProjectV2View(input: { projectId: $pid, name: $name, layout: $layout }) {
                  projectV2View { id name }
                }
              }""", {"pid": pid, "name": name, "layout": layout})
            print(f"  ✅ {name} ({layout})")
        except Exception as e:
            print(f"  ⚠️  {name} 실패: {e}")

    # ── 6. Issue 연결 ──
    print("[5] Issue 연결 + 필드 값 설정...")
    with open("/home/user/webapp/issues_result.json") as f:
        issues = json.load(f)

    def set_val(item_id, field_id, value):
        gql(token, """
          mutation($pid: ID!, $iid: ID!, $fid: ID!, $val: ProjectV2FieldValue!) {
            updateProjectV2ItemFieldValue(input: {
              projectId: $pid, itemId: $iid, fieldId: $fid, value: $val
            }) { projectV2Item { id } }
          }""", {"pid": pid, "iid": item_id, "fid": field_id, "val": value})

    for iss in issues:
        # 프로젝트에 추가
        r = gql(token, """
          mutation($pid: ID!, $cid: ID!) {
            addProjectV2ItemById(input: { projectId: $pid, contentId: $cid }) {
              item { id }
            }
          }""", {"pid": pid, "cid": iss["node_id"]})
        item_id = r["addProjectV2ItemById"]["item"]["id"]

        # Status = Backlog
        set_val(item_id, status_fid, {"singleSelectOptionId": backlog_oid})

        # Priority
        p_id = priority_opts.get(iss["priority"])
        if p_id:
            set_val(item_id, pf["id"], {"singleSelectOptionId": p_id})

        # Start / End date
        set_val(item_id, start_fid, {"date": iss["start"]})
        set_val(item_id, end_fid,   {"date": iss["end"]})

        print(f"  ✅ #{iss['number']} [{iss['priority']}] {iss['title'][:50]}...")
        time.sleep(0.25)

    # ── 결과 저장 ──
    result = {"project_url": purl, "issues_url": f"https://github.com/{OWNER}/{REPO}/issues"}
    with open("/home/user/webapp/project_result.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 55)
    print("✅ 모든 작업 완료!")
    print(f"\n🔗 Project: {purl}")
    print(f"📋 Issues : https://github.com/{OWNER}/{REPO}/issues")
    print("=" * 55)

if __name__ == "__main__":
    main()
