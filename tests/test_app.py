#!/usr/bin/env python3
"""
Automated Test Suite for Morphogenesis WebGL Engine
Tests shader compilation, WebGL program linking, UI localization,
and all interactive buttons/controls using Playwright headless browser.
"""

import asyncio
import os
import socket
import subprocess
import sys
import time
from playwright.async_api import async_playwright

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

async def run_tests():
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
            page = await browser.new_page()

            console_logs = []
            page_errors = []
            page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            print(f"🚀 Loading Morphogenesis Engine on http://localhost:{port}/ ...")
            await page.goto(f"http://localhost:{port}/", timeout=10000)
            await asyncio.sleep(1.2)

            # 1. Shader & Console Check
            print("\n[1/7] Testing WebGL Shader Compilation & Linking...")
            shader_errs = [l for l in console_logs if "shader" in l.lower() or "not linked" in l.lower() or "not valid" in l.lower()]
            if shader_errs:
                err_msg = f"Shader errors detected: {shader_errs}"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")
            else:
                passed_tests.append("WebGL Shader Compilation & Linking")
                print("  ✓ WebGL Shaders compiled & linked with 0 errors")

            # 2. UI Localization Check
            print("\n[2/7] Testing UI Localization Dictionary...")
            i18n_ready = await page.evaluate("typeof t === 'function' && t('app.title') === 'MORPHOGENESIS'")
            phase11_title = await page.evaluate("t('phases.11.title')")
            if i18n_ready and "Beach" in phase11_title:
                passed_tests.append("UI Localization System")
                print(f"  ✓ Localization loaded: '{phase11_title}'")
            else:
                err_msg = "Localization failed or missing 'Beach' in Phase 11"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")

            # 3. Zen Mode Full Cycle
            print("\n[3/7] Testing Pure Zen Cinema Mode...")
            zen_btn = await page.wait_for_selector("#topZenBtn", timeout=3000)
            await zen_btn.click()
            await asyncio.sleep(0.3)
            is_zen = await page.evaluate("state.zenMode")
            zen_visible = await page.evaluate("!document.getElementById('zenModeOverlay').classList.contains('ui-force-hidden')")
            
            # Click Zen Center Play
            zen_play = await page.wait_for_selector("#zenCenterPlayBtn", timeout=3000)
            await zen_play.click()
            await asyncio.sleep(0.2)
            auto_cruise = await page.evaluate("state.autoCruise")

            # Click Zen Exit
            zen_exit = await page.wait_for_selector("#zenExitBtn", timeout=3000)
            await zen_exit.click()
            await asyncio.sleep(0.3)
            is_zen_after = await page.evaluate("state.zenMode")
            top_restored = await page.evaluate("!document.getElementById('topHeaderBar').classList.contains('ui-force-hidden')")

            if is_zen and zen_visible and auto_cruise and not is_zen_after and top_restored:
                passed_tests.append("Zen Mode Enter, Auto-Zoom & Exit")
                print("  ✓ Zen Mode activated, center auto-zoom started, and exited cleanly")
            else:
                err_msg = f"Zen Mode failed cycle: is_zen={is_zen}, auto_cruise={auto_cruise}, is_zen_after={is_zen_after}"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")

            # 4. Transport Controls & Speed Presets
            print("\n[4/7] Testing Auto-Zoom Transport, Speeds & Direction...")
            cruise_btn = await page.wait_for_selector("#cruiseBtn")
            await cruise_btn.click()
            
            spd_checks = []
            for spd_id, val in [("spd05", 0.5), ("spd10", 1.0), ("spd20", 2.0), ("spd40", 4.0)]:
                btn = await page.wait_for_selector(f"#{spd_id}")
                await btn.click()
                spd = await page.evaluate("state.cruiseSpeed")
                spd_checks.append(abs(spd - val) < 0.01)

            # Direction toggle
            dir_btn = await page.wait_for_selector("#dirBtn")
            d1 = await page.evaluate("state.cruiseDir")
            await dir_btn.click()
            d2 = await page.evaluate("state.cruiseDir")

            if all(spd_checks) and d1 != d2:
                passed_tests.append("Auto-Zoom Transport, Speed Pills & Direction")
                print("  ✓ Transport play/pause, 0.5x..4x speeds, and direction toggled")
            else:
                err_msg = f"Transport check failed: spd_checks={spd_checks}, dir_toggle={d1 != d2}"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")

            # 5. UI Panel Collapse & Reseed
            print("\n[5/7] Testing UI Collapse/Restore & Procedural Seed Mutation...")
            hide_btn = await page.wait_for_selector("#topToggleUIBtn")
            await hide_btn.click()
            await asyncio.sleep(0.2)
            hud_hidden = await page.evaluate("document.getElementById('bottomHudContainer').classList.contains('ui-force-hidden')")
            float_btn = await page.wait_for_selector("#floatingShowUIBtn")
            await float_btn.click()
            await asyncio.sleep(0.2)
            hud_restored = await page.evaluate("!document.getElementById('bottomHudContainer').classList.contains('ui-force-hidden')")

            s1 = await page.evaluate("state.seed")
            reseed_btn = await page.wait_for_selector("button[onclick*='reseedApp()']")
            await reseed_btn.click()
            s2 = await page.evaluate("state.seed")

            if hud_hidden and hud_restored and s1 != s2:
                passed_tests.append("Bottom UI Hide/Restore & Seed Mutation")
                print(f"  ✓ Bottom UI collapsed/restored; Seed mutated: #{hex(s1)} → #{hex(s2)}")
            else:
                err_msg = f"UI collapse or reseed failed: hud_hidden={hud_hidden}, hud_restored={hud_restored}, seed_diff={s1 != s2}"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")

            # 6. Stage Tabs & Phase Stepper Breadcrumbs
            print("\n[6/7] Testing Stage Tabs (I, II, III) & Phase Steppers...")
            tab_checks = []
            for tab_id, z_val in [("#tabStage2", 210), ("#tabStage3", 585), ("#tabStage1", 0)]:
                tab = await page.wait_for_selector(tab_id)
                await tab.click()
                cur_z = await page.evaluate("state.targetZoomZ")
                tab_checks.append(abs(cur_z - z_val) < 1.0)

            step_checks = []
            for step_id, min_z, max_z in [("#stepP6", 200, 250), ("#stepP11", 650, 680), ("#stepP1", 0, 10)]:
                step = await page.wait_for_selector(step_id)
                await step.click()
                cur_z = await page.evaluate("state.targetZoomZ")
                step_checks.append(min_z <= cur_z <= max_z)

            if all(tab_checks) and all(step_checks):
                passed_tests.append("Stage Switcher Tabs & 16-Phase Breadcrumbs")
                print("  ✓ Stage tabs and phase breadcrumbs jump camera accurately")
            else:
                err_msg = f"Stage tabs or stepper breadcrumbs failed: tab_checks={tab_checks}, step_checks={step_checks}"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")

            # 7. Simulation Toggles & Fly.io Modal
            print("\n[7/7] Testing Life / Drift Toggles & Fly.io Deployment Modal...")
            life_btn = await page.wait_for_selector("#btnToggleLife")
            l1 = await page.evaluate("state.lifeEnabled")
            await life_btn.click()
            l2 = await page.evaluate("state.lifeEnabled")

            drift_btn = await page.wait_for_selector("#btnToggleDrift")
            dr1 = await page.evaluate("state.colorDrift")
            await drift_btn.click()
            dr2 = await page.evaluate("state.colorDrift")

            fly_btn = await page.wait_for_selector("button[onclick*='openFlyModal()']")
            await fly_btn.click()
            await asyncio.sleep(0.2)
            modal_open = await page.evaluate("!document.getElementById('flyModal').classList.contains('ui-force-hidden')")
            
            # Switch tab in Fly Modal
            tab_toml = await page.wait_for_selector("#flyTab_flytoml")
            await tab_toml.click()
            toml_text = await page.evaluate("document.getElementById('flyCodeBlock').textContent")
            has_toml = "app = " in toml_text or "fly.toml" in toml_text

            close_fly = await page.wait_for_selector("#flyModal button[onclick*='closeFlyModal()']")
            await close_fly.click()
            await asyncio.sleep(0.2)
            modal_closed = await page.evaluate("document.getElementById('flyModal').classList.contains('ui-force-hidden')")

            if (l1 != l2) and (dr1 != dr2) and modal_open and has_toml and modal_closed:
                passed_tests.append("Aperiodic Life, Color Drift & Fly.io Modal Kit")
                print("  ✓ Conway Life, color drift toggles, and Fly.io modal tabs passed")
            else:
                err_msg = f"Toggles or Fly Modal failed: life={l1!=l2}, drift={dr1!=dr2}, modal_open={modal_open}, modal_closed={modal_closed}"
                errors.append(err_msg)
                print(f"  ❌ {err_msg}")

            await browser.close()
    finally:
        server.kill()

    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY:")
    for t_name in passed_tests:
        print(f"  [PASS] {t_name}")
    print("=" * 60)

    if errors:
        print(f"\n❌ {len(errors)} TEST(S) FAILED:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print(f"\n🎉 ALL {len(passed_tests)} TEST SUITES PASSED CLEANLY!")
        return True

if __name__ == '__main__':
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
