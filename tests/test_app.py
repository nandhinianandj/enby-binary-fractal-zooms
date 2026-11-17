#!/usr/bin/env python3
"""
Automated Test Suite for Morphogenesis WebGL Engine
Verifies shader compilation, WebGL linking, UI localization, HTTP headers,
and tests ALL 47 interactive buttons and controls across BOTH Production (/) and Development (/dev) environments.
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from playwright.async_api import async_playwright

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

async def verify_environment_buttons(page, env_name, target_url, errors):
    """
    Exhaustively clicks and tests every single button, pill, tab, toggle,
    and modal control on the given environment (Prod or Dev).
    """
    print(f"\n" + "-"*55)
    print(f"  🔍 RUNNING BUTTON & CONTROL SUITE ON {env_name.upper()} ({target_url})")
    print("-"*55)

    await page.goto(target_url, timeout=10000)
    await asyncio.sleep(1.0)

    # 1. Environment Badge & Switcher Link Check
    if env_name == "Production":
        has_dev_badge = await page.evaluate("!!document.getElementById('devBadge')")
        dev_link = await page.query_selector('a[href="/dev"]')
        if has_dev_badge or not dev_link:
            errors.append(f"[{env_name}] Prod should not have devBadge and must have link to /dev")
        else:
            print(f"  ✓ [{env_name}] Environment header correctly links to Dev (/dev)")
    else:
        has_dev_badge = await page.evaluate("!!document.getElementById('devBadge')")
        prod_link = await page.query_selector('a[href="/"]')
        badge_text = await page.evaluate("document.getElementById('devBadge')?.textContent || ''")
        if not has_dev_badge or not prod_link or "DEV" not in badge_text:
            errors.append(f"[{env_name}] Dev must show devBadge ('DEV') and link to /")
        else:
            print(f"  ✓ [{env_name}] Environment header correctly displays '{badge_text}' and links to Prod (/)")

    # 2. Pure Zen Mode Buttons (4 clicks)
    zen_btn = await page.wait_for_selector("#topZenBtn", timeout=3000)
    await zen_btn.click()
    await asyncio.sleep(0.2)
    zen_active = await page.evaluate("state.zenMode")
    overlay_visible = await page.evaluate("!document.getElementById('zenModeOverlay').classList.contains('ui-force-hidden')")
    
    zen_play = await page.wait_for_selector("#zenCenterPlayBtn", timeout=3000)
    await zen_play.click()
    await asyncio.sleep(0.1)
    cruise_on = await page.evaluate("state.autoCruise")
    await zen_play.click()
    await asyncio.sleep(0.1)
    cruise_off = await page.evaluate("state.autoCruise")

    zen_exit = await page.wait_for_selector("#zenExitBtn", timeout=3000)
    await zen_exit.click()
    await asyncio.sleep(0.2)
    zen_inactive = await page.evaluate("state.zenMode")
    header_restored = await page.evaluate("!document.getElementById('topHeaderBar').classList.contains('ui-force-hidden')")

    if zen_active and overlay_visible and cruise_on and not cruise_off and not zen_inactive and header_restored:
        print(f"  ✓ [{env_name}] Zen buttons passed (#topZenBtn, #zenCenterPlayBtn, #zenExitBtn)")
    else:
        errors.append(f"[{env_name}] Zen mode button interaction failed")

    # 3. Transport Controls & Speed Presets (8 clicks)
    cruise_btn = await page.wait_for_selector("#cruiseBtn")
    await cruise_btn.click()
    await asyncio.sleep(0.1)
    c1 = await page.evaluate("state.autoCruise")
    await cruise_btn.click()
    await asyncio.sleep(0.1)
    c2 = await page.evaluate("state.autoCruise")

    speeds_ok = True
    for spd_id, val in [("spd05", 0.5), ("spd10", 1.0), ("spd20", 2.0), ("spd40", 4.0)]:
        s_btn = await page.wait_for_selector(f"#{spd_id}")
        await s_btn.click()
        cur_spd = await page.evaluate("state.cruiseSpeed")
        if abs(cur_spd - val) > 0.01:
            speeds_ok = False

    dir_btn = await page.wait_for_selector("#dirBtn")
    d_initial = await page.evaluate("state.cruiseDir")
    await dir_btn.click()
    d_inverted = await page.evaluate("state.cruiseDir")
    await dir_btn.click()
    d_restored = await page.evaluate("state.cruiseDir")

    if c1 and not c2 and speeds_ok and (d_initial != d_inverted) and (d_initial == d_restored):
        print(f"  ✓ [{env_name}] Transport & Speed pills passed (#cruiseBtn, 0.5x..4x, #dirBtn)")
    else:
        errors.append(f"[{env_name}] Transport or speed controls failed")

    # 4. UI Collapse & Reseed Buttons (5 clicks)
    hide_top_btn = await page.wait_for_selector("#topToggleUIBtn")
    await hide_top_btn.click()
    await asyncio.sleep(0.15)
    hud_h1 = await page.evaluate("document.getElementById('bottomHudContainer').classList.contains('ui-force-hidden')")
    float_btn = await page.wait_for_selector("#floatingShowUIBtn")
    await float_btn.click()
    await asyncio.sleep(0.15)
    hud_r1 = await page.evaluate("!document.getElementById('bottomHudContainer').classList.contains('ui-force-hidden')")

    bottom_hide = await page.wait_for_selector("#bottomHideUIBtn")
    await bottom_hide.click()
    await asyncio.sleep(0.15)
    hud_h2 = await page.evaluate("document.getElementById('bottomHudContainer').classList.contains('ui-force-hidden')")
    await float_btn.click()
    await asyncio.sleep(0.15)
    hud_r2 = await page.evaluate("!document.getElementById('bottomHudContainer').classList.contains('ui-force-hidden')")

    s_before = await page.evaluate("state.seed")
    reseed_btn = await page.wait_for_selector("button[onclick*='reseedApp()']")
    await reseed_btn.click()
    s_after = await page.evaluate("state.seed")

    if hud_h1 and hud_r1 and hud_h2 and hud_r2 and (s_before != s_after):
        print(f"  ✓ [{env_name}] UI collapse & Mutate Seed passed (#topToggleUIBtn, #floatingShowUIBtn, #bottomHideUIBtn, reseed)")
    else:
        errors.append(f"[{env_name}] UI collapse or seed mutation failed")

    # 5. Stage Switcher Tabs (3 clicks)
    stage_tabs = [("#tabStage2", 210), ("#tabStage3", 585), ("#tabStage1", 0)]
    tabs_ok = True
    for tab_id, z_target in stage_tabs:
        tab_elem = await page.wait_for_selector(tab_id)
        await tab_elem.click()
        z_val = await page.evaluate("state.targetZoomZ")
        if abs(z_val - z_target) > 1.0:
            tabs_ok = False
    if tabs_ok:
        print(f"  ✓ [{env_name}] Stage Tabs I, II, III passed (#tabStage1..3)")
    else:
        errors.append(f"[{env_name}] Stage switcher tabs failed")

    # 6. All 16 Phase Stepper Breadcrumb Buttons (16 clicks)
    phase_targets = [
        ("#stepP1", 0), ("#stepP2", 55), ("#stepP3", 95), ("#stepP4", 135),
        ("#stepP5", 168), ("#stepP6", 220), ("#stepP7", 320), ("#stepP8", 420),
        ("#stepP9", 515), ("#stepP10", 595), ("#stepP11", 665), ("#stepP12", 735),
        ("#stepP13", 795), ("#stepP14", 860), ("#stepP15", 930), ("#stepP16", 990)
    ]
    steppers_ok = True
    for step_id, exp_z in phase_targets:
        step_btn = await page.wait_for_selector(step_id)
        await step_btn.click()
        z_val = await page.evaluate("state.targetZoomZ")
        if abs(z_val - exp_z) > 1.0:
            steppers_ok = False
            errors.append(f"[{env_name}] {step_id} failed to jump to Z={exp_z} (actual={z_val})")
    if steppers_ok:
        print(f"  ✓ [{env_name}] All 16 Phase Steppers passed (#stepP1 through #stepP16)")

    # 7. Simulation Toggles & Controls (3 clicks)
    life_btn = await page.wait_for_selector("#btnToggleLife")
    l_init = await page.evaluate("state.lifeEnabled")
    await life_btn.click()
    l_after = await page.evaluate("state.lifeEnabled")

    rand_life = await page.wait_for_selector("button[onclick*='randomizeBinaryLife()']")
    await rand_life.click()

    drift_btn = await page.wait_for_selector("#btnToggleDrift")
    dr_init = await page.evaluate("state.colorDrift")
    await drift_btn.click()
    dr_after = await page.evaluate("state.colorDrift")

    if (l_init != l_after) and (dr_init != dr_after):
        print(f"  ✓ [{env_name}] Simulation Toggles passed (#btnToggleLife, randomizeLife, #btnToggleDrift)")
    else:
        errors.append(f"[{env_name}] Life or color drift toggles failed")

    # 8. Fly.io Modal Tabs, Copy & Close (7 clicks)
    fly_open = await page.wait_for_selector("button[onclick*='openFlyModal()']")
    await fly_open.click()
    await asyncio.sleep(0.15)
    modal_open = await page.evaluate("!document.getElementById('flyModal').classList.contains('ui-force-hidden')")

    modal_tabs_ok = True
    for tab_id, snippet_key in [
        ("#flyTab_flytoml", "app ="),
        ("#flyTab_server", "http.createServer"),
        ("#flyTab_cli", "fly launch"),
        ("#flyTab_dockerfile", "FROM node")
    ]:
        m_tab = await page.wait_for_selector(tab_id)
        await m_tab.click()
        code_txt = await page.evaluate("document.getElementById('flyCodeBlock').textContent")
        if snippet_key not in code_txt:
            modal_tabs_ok = False
            errors.append(f"[{env_name}] Fly modal tab {tab_id} missing keyword '{snippet_key}'")

    copy_btn = await page.wait_for_selector("button[onclick*='copyFlySnippet()']")
    await copy_btn.click()
    confirm_txt = await page.evaluate("document.getElementById('copyConfirm').textContent")
    copy_ok = "Copied" in confirm_txt

    fly_close = await page.wait_for_selector("#flyModal button[onclick*='closeFlyModal()']")
    await fly_close.click()
    await asyncio.sleep(0.15)
    modal_closed = await page.evaluate("document.getElementById('flyModal').classList.contains('ui-force-hidden')")

    if modal_open and modal_tabs_ok and copy_ok and modal_closed:
        print(f"  ✓ [{env_name}] Fly.io Modal passed (open, 4 tabs, copy snippet, close)")
    else:
        errors.append(f"[{env_name}] Fly.io modal controls failed")

    # 9. Cross-Environment Navigation Link Click (1 click)
    if env_name == "Production":
        nav_link = await page.wait_for_selector('a[href="/dev"]')
        await nav_link.click()
        await asyncio.sleep(0.5)
        cur_url = page.url
        has_dev_badge_now = await page.evaluate("!!document.getElementById('devBadge')")
        if "/dev" in cur_url and has_dev_badge_now:
            print(f"  ✓ [{env_name}] Navigated successfully to Development (/dev) via header link")
        else:
            errors.append(f"[{env_name}] Clicking /dev link did not arrive at dev environment")
    else:
        nav_link = await page.wait_for_selector('a[href="/"]')
        await nav_link.click()
        await asyncio.sleep(0.5)
        cur_url = page.url
        has_dev_badge_now = await page.evaluate("!!document.getElementById('devBadge')")
        if cur_url.rstrip('/').endswith(f":{port}") and not has_dev_badge_now:
            print(f"  ✓ [{env_name}] Navigated successfully to Production (/) via header link")
        else:
            errors.append(f"[{env_name}] Clicking / link did not arrive at prod environment")

async def run_tests():
    global port
    port = str(find_free_port())
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server = subprocess.Popen(
        ['node', 'server.js'],
        cwd=root_dir,
        env=dict(os.environ, PORT=port),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(0.8)

    errors = []
    passed_tests = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--use-gl=angle', '--use-angle=swiftshader', '--no-sandbox']
            )
            context = await browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = await context.new_page()

            console_logs = []
            page_errors = []
            page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            # HTTP Routing & Headers Verification
            print(f"🚀 Verifying HTTP Endpoints on http://localhost:{port}/ ...")
            prod_req = urllib.request.Request(f"http://localhost:{port}/")
            with urllib.request.urlopen(prod_req) as prod_resp:
                prod_status = prod_resp.status
                prod_env = prod_resp.headers.get("X-Environment")

            dev_req = urllib.request.Request(f"http://localhost:{port}/dev")
            with urllib.request.urlopen(dev_req) as dev_resp:
                dev_status = dev_resp.status
                dev_env = dev_resp.headers.get("X-Environment")
                dev_cache = dev_resp.headers.get("Cache-Control")

            health_req = urllib.request.Request(f"http://localhost:{port}/healthz")
            with urllib.request.urlopen(health_req) as health_resp:
                health_data = json.loads(health_resp.read().decode('utf-8'))

            if (prod_status == 200 and prod_env == 'production' and
                dev_status == 200 and dev_env == 'development' and
                'no-cache' in (dev_cache or '') and
                health_data.get('endpoints', {}).get('development') == '/dev'):
                passed_tests.append("HTTP Endpoint Routing & Headers")
                print("  ✓ / -> 200 OK [X-Environment: production]")
                print("  ✓ /dev -> 200 OK [X-Environment: development, no-cache]")
                print(f"  ✓ /healthz -> 200 OK {health_data['endpoints']}")
            else:
                errors.append(f"Endpoint checks failed: prod_env={prod_env}, dev_env={dev_env}")

            # Verify WebGL Shaders & UI Localization
            await page.goto(f"http://localhost:{port}/", timeout=10000)
            await asyncio.sleep(1.0)
            shader_errs = [l for l in console_logs if "shader" in l.lower() or "not linked" in l.lower() or "not valid" in l.lower()]
            if shader_errs:
                errors.append(f"Shader errors: {shader_errs}")
            else:
                passed_tests.append("WebGL Shader Compilation & Linking")
                print("  ✓ WebGL Shaders compiled & linked with 0 errors")

            i18n_ok = await page.evaluate("typeof t === 'function' && t('app.title') === 'MORPHOGENESIS'")
            if i18n_ok:
                passed_tests.append("UI Localization System")
                print("  ✓ Localization dictionary loaded")
            else:
                errors.append("Localization dictionary failed to load")

            # Exhaustive Button Clicks on Production (/)
            await verify_environment_buttons(page, "Production", f"http://localhost:{port}/", errors)
            if not errors:
                passed_tests.append("All 47 Button Clicks on Production (/)")

            # Exhaustive Button Clicks on Development (/dev)
            pre_dev_error_count = len(errors)
            await verify_environment_buttons(page, "Development", f"http://localhost:{port}/dev", errors)
            if len(errors) == pre_dev_error_count:
                passed_tests.append("All 47 Button Clicks on Development (/dev)")

            await browser.close()
    finally:
        server.kill()

    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY:")
    for t_name in passed_tests:
        print(f"  [PASS] {t_name}")
    print("=" * 60)

    if errors:
        print(f"\n❌ {len(errors)} ERROR(S) DETECTED:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"\n🎉 ALL BUTTON CLICKS & CONTROLS VERIFIED ON BOTH PROD AND DEV!")
        return True

if __name__ == '__main__':
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
