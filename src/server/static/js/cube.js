import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

/**
 * Mounts the Glowing Cube into a specific DOM element.
 * @param {HTMLElement} container - The div where the canvas should be injected.
 * @returns {Object} - An API to control the cube (setColor, destroy, etc.)
 */
export function mountGlowingCube(container) {
    if (!container) return null;

    // Helper to parse hex color with optional white channel (e.g. #RRGGBBAA) -- DOUBLE CHECK
    const parseHexRGBW = (hexColor) => {
        if (!hexColor || typeof hexColor !== 'string' || !/^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$/.test(hexColor)) {
            return {rgb: new THREE.Color(0xffaa00), white: 1};
        }

        const cleaned = hexColor.replace('#', '');
        const rgb = new THREE.Color(`#${cleaned.slice(0, 6)}`);
        const white = cleaned.length === 8 ? parseInt(cleaned.slice(6), 16) / 255 : 1;

        return { rgb, white };
    };

    try {
        // 1. SETUP
        // Prevent 0x0 dimension crashes by forcing a minimum of 1 pixel
        const width = Math.max(1, container.clientWidth);
        const height = Math.max(1, container.clientHeight);

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x161514);

    const camera = new THREE.PerspectiveCamera(35, width / height, 0.1, 100);
    camera.position.set(0, 0, 14);

    const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;

    // Clear previous canvas if any
    container.innerHTML = '';
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

    // 3. OBJECTS
    const shellGeometry = new RoundedBoxGeometry(3.2, 3.2, 3.2, 16, 0.5);
    const shellMaterial = new THREE.MeshPhysicalMaterial({
        color: 0xffffff,
        transmission: 1.25,
        opacity: 1.25,
        metalness: 0.05,
        roughness: 0.5,
        ior: 2.5,
        thickness: 2.0,
        attenuationColor: 0xffaa00,
        attenuationDistance: 2.0,
        specularIntensity: 1.0,
        transparent: true,
        side: THREE.DoubleSide
    });
    const shellCube = new THREE.Mesh(shellGeometry, shellMaterial);
    scene.add(shellCube);

    const lightsGroup = new THREE.Group();
    scene.add(lightsGroup);

    // Helper to create lights
    function addLight(x, y, z) {
        const l = new THREE.DirectionalLight(0xffaa00, 2);
        l.position.set(x, y, z);
        lightsGroup.add(l);
    }
    addLight(0, 10, 0); addLight(0, -10, 0); addLight(-10, 0, 0); addLight(10, 0, 0);

    const coreMaterial = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
    const coreCube = new THREE.Mesh(new RoundedBoxGeometry(2.2, 2.2, 2.2, 16, 0.4), coreMaterial);
    shellCube.add(coreCube);

    const coreLight = new THREE.PointLight(0xffaa00, 15, 20);
    shellCube.add(coreLight);

    // 4. STATE
    let isDragging = false;
    let isBreathing = true;
    let isActive = true; // Controls the animation loop
    let previousPosition = { x: 0, y: 0 };
    let targetRotationX = 0;
    let targetRotationY = 0;
    let mouseX = 0;
    let mouseY = 0;

    // 5. EVENT HANDLERS
    // Defined inside scope to access variables, but named for removal later
    const onStart = (x, y) => {
        isDragging = true;
        previousPosition = { x, y };
    };

    const onMove = (x, y) => {
        if (isDragging) {
            const deltaX = x - previousPosition.x;
            const deltaY = y - previousPosition.y;
            // Upside down check
            const rotateDirection = Math.cos(targetRotationX) > 0 ? 1 : -1;
            targetRotationY += (deltaX * 0.005) * rotateDirection;
            targetRotationX += deltaY * 0.005;
            previousPosition = { x, y };
        }
        // Parallax
        const rect = container.getBoundingClientRect();
        mouseX = (x - rect.left - (rect.width/2)) * 0.0001;
        mouseY = (y - rect.top - (rect.height/2)) * 0.0001;
    };

    const onEnd = () => { isDragging = false; };

    // Listeners
    const handleMouseDown = (e) => onStart(e.clientX, e.clientY);
    const handleMouseMove = (e) => onMove(e.clientX, e.clientY);
    const handleMouseUp = onEnd;

    const handleTouchStart = (e) => onStart(e.touches[0].clientX, e.touches[0].clientY);
    const handleTouchMove = (e) => {
        if(e.cancelable) e.preventDefault();
        onMove(e.touches[0].clientX, e.touches[0].clientY);
    };
    const handleTouchEnd = onEnd;

    // Attach to Container (mostly) and Window (for drag release)
    container.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    window.addEventListener('touchend', handleTouchEnd);

    // 6. ANIMATION LOOP
    const clock = new THREE.Clock();

    function animate() {
        if (!isActive) return; // Stop loop if destroyed

        requestAnimationFrame(animate);
        const time = clock.getElapsedTime();

        const dragFactor = 0.05;
        shellCube.rotation.x += ((targetRotationX + mouseY * 20) - shellCube.rotation.x) * dragFactor;
        shellCube.rotation.y += ((targetRotationY + mouseX * 20) - shellCube.rotation.y) * dragFactor;

        let targetScale = 1.0;
        let targetIntensity = 1;

        if (isBreathing) {
            const pulse = Math.sin(time * 1);
            targetScale = 0.9 + (pulse * 0.15);
            targetIntensity = -1 + (pulse * 25);
        }

        coreCube.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
        coreLight.intensity += (targetIntensity - coreLight.intensity) * 0.1;

        composer.render();
    }
    animate();

    // 7. RESIZE OBSERVER
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            const w = Math.max(1, entry.contentRect.width);
            const h = Math.max(1, entry.contentRect.height);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
            composer.setSize(w, h);
        }
    });
    resizeObserver.observe(container);

    // 8. PUBLIC API (The "Remote Control")
    return {
        setColor: (hexColor) => {
            const parsed = parseHexRGBW(hexColor);
            const baseColor = parsed.rgb;
            const whiteIntensity = parsed.white;

            shellMaterial.attenuationColor.set(baseColor);
            coreMaterial.color.set(baseColor);
            coreLight.color.set(baseColor);

            // Mix with white channel to boost brightness and keep hue
            const whiteColor = new THREE.Color(0xffffff);
            const mixedColor = baseColor.clone().lerp(whiteColor, whiteIntensity * 0.35);

            lightsGroup.children.forEach(l => {
                l.color.set(mixedColor);
                l.intensity = 2 + whiteIntensity * 2;
            });

            coreLight.intensity = 10 + whiteIntensity * 15;
        },
        setBreathing: (state) => {
            isBreathing = Boolean(state);
        },
        toggleBreathing: () => {
            isBreathing = !isBreathing;
            return isBreathing; // Return state so UI can update text
        },
        destroy: () => {
            isActive = false; // Stop animation loop
            resizeObserver.disconnect();

            // Remove Listeners
            container.removeEventListener('mousedown', handleMouseDown);
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
            container.removeEventListener('touchstart', handleTouchStart);
            container.removeEventListener('touchmove', handleTouchMove);
            window.removeEventListener('touchend', handleTouchEnd);

            // Clean up Three.js memory
            renderer.dispose();
            composer.dispose();
            container.innerHTML = '';
        }
    };

    } catch (error) {
        console.error('Cube initialization failed:', error);
        container.innerHTML = '<div class="cube-error">Cube failed to initialize. Please reload.</div>';

        return {
            setColor: () => undefined,
            setBreathing: () => undefined,
            toggleBreathing: () => false,
            destroy: () => { container.innerHTML = ''; }
        };
    }
}