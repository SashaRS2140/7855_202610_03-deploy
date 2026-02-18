import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

document.addEventListener("DOMContentLoaded", function() {

    const container = document.getElementById('canvas-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. SCENE SETUP
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);

    const camera = new THREE.PerspectiveCamera(35, width / height, 0.1, 100);
    camera.position.set(0, 0, 14);

    const renderer = new THREE.WebGLRenderer({ antialias: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    container.appendChild(renderer.domElement);

    // 2. POST-PROCESSING
    const renderScene = new RenderPass(scene, camera);
    const bloomPass = new UnrealBloomPass(new THREE.Vector2(width, height), 1.5, 0.4, 0.85);
    bloomPass.threshold = 0.1;
    bloomPass.strength = 1.2;
    bloomPass.radius = 0.75;

    const composer = new EffectComposer(renderer);
    composer.addPass(renderScene);
    composer.addPass(bloomPass);

    // 3. OUTER SHELL
    const shellGeometry = new RoundedBoxGeometry(3.2, 3.2, 3.2, 16, 0.5);
    const shellMaterial = new THREE.MeshPhysicalMaterial({
        color: 0xffffff,
        transmission: 1.25,
        opacity: 1.25,
        metalness: 0.05,
        roughness: 0.5,
        ior: 2.5,
        thickness: 2.0,
        attenuationColor: 0xffaa00, // Initial Color
        attenuationDistance: 2.0,
        specularIntensity: 1.0,
        transparent: true,
        side: THREE.DoubleSide
    });
    const shellCube = new THREE.Mesh(shellGeometry, shellMaterial);
    scene.add(shellCube);

    // 4. LIGHTS (Grouped for easy color updating)
    const lightsGroup = new THREE.Group();
    scene.add(lightsGroup);

    function createRimLight(x, y, z) {
        const light = new THREE.DirectionalLight(0xffaa00, 2);
        light.position.set(x, y, z);
        lightsGroup.add(light);
        return light;
    }

    const topLight = createRimLight(0, 10, 0);
    const bottomLight = createRimLight(0, -10, 0);
    const leftLight = createRimLight(-10, 0, 0);
    const rightLight = createRimLight(10, 0, 0);

    // 5. INNER CORE
    const coreGeometry = new RoundedBoxGeometry(2.2, 2.2, 2.2, 16, 0.4);
    const coreMaterial = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
    const coreCube = new THREE.Mesh(coreGeometry, coreMaterial);
    shellCube.add(coreCube);

    const coreLight = new THREE.PointLight(0xffaa00, 15, 20);
    shellCube.add(coreLight);

    // ---------------------------------------------------------
    // NEW: COLOR PICKER LOGIC
    // ---------------------------------------------------------
    const colorPicker = document.getElementById('cube-color');

    if (colorPicker) {
        colorPicker.addEventListener('input', (event) => {
            const hexColor = event.target.value;
            const newColor = new THREE.Color(hexColor);

            // 1. Update Shell Tint
            shellMaterial.attenuationColor.set(newColor);

            // 2. Update Core Appearance
            coreMaterial.color.set(newColor);
            coreLight.color.set(newColor);

            // 3. Update All Rim Lights
            lightsGroup.children.forEach(light => {
                if(light.isLight) light.color.set(newColor);
            });
        });
    }

    // 6. INTERACTION LOGIC
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let targetRotationX = 0;
    let targetRotationY = 0;
    let mouseX = 0;
    let mouseY = 0;
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        // Calculate mouse relative to container, not window, for better reusability
        mouseX = (e.clientX - rect.left - (rect.width/2)) * 0.0001;
        mouseY = (e.clientY - rect.top - (rect.height/2)) * 0.0001;

        if (isDragging) {
            const deltaMove = {
                x: e.clientX - previousMousePosition.x,
                y: e.clientY - previousMousePosition.y
            };
            targetRotationY += deltaMove.x * 0.005;
            targetRotationX += deltaMove.y * 0.005;
        }
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    container.addEventListener('mousedown', () => { isDragging = true; }); // Listen on container only
    window.addEventListener('mouseup', () => { isDragging = false; }); // Listen on window to catch drags outside

    // 7. BREATHING LOGIC
    let isBreathing = true;
    const toggleBtn = document.getElementById('toggle-breath');
    if(toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            isBreathing = !isBreathing;
            toggleBtn.innerText = isBreathing ? "Turn Breathing OFF" : "Turn Breathing ON";
        });
    }

    // 8. ANIMATION LOOP
    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const time = clock.getElapsedTime();

        // Smooth Rotation
        const dragFactor = 0.05;
        const finalTargetX = targetRotationX + (mouseY * 20);
        const finalTargetY = targetRotationY + (mouseX * 20);
        shellCube.rotation.x += (finalTargetX - shellCube.rotation.x) * dragFactor;
        shellCube.rotation.y += (finalTargetY - shellCube.rotation.y) * dragFactor;

        // Breathing
        let targetScale = 1.0;
        let targetIntensity = 15;

        if (isBreathing) {
            const pulse = Math.sin(time * 2);
            targetScale = 0.9 + (pulse * 0.05);
            targetIntensity = 15 + (pulse * 5); // Reduced intensity swing slightly for stability
        }

        coreCube.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
        coreLight.intensity += (targetIntensity - coreLight.intensity) * 0.1;

        composer.render();
    }

    animate();

    // 9. ROBUST RESIZING (Best Practice for Scalability)
    // Using ResizeObserver handles cases where the div changes size (e.g. sidebar open),
    // not just when the whole window resizes.
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            const newWidth = entry.contentRect.width;
            const newHeight = entry.contentRect.height;

            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();

            renderer.setSize(newWidth, newHeight);
            composer.setSize(newWidth, newHeight);
        }
    });

    resizeObserver.observe(container);
});