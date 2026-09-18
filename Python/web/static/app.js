async function getJSON(url) {
    const response = await fetch(url, { cache: "no-store" });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
}

function formatTimestamp(timestamp) {
    if (!timestamp) return "—";

    const value = String(timestamp);
    const match = value.match(
        /^(\d{4}-\d{2}-\d{2})[T ](\d{2}):(\d{2}):(\d{2})/
    );

    if (match) {
        return `${match[1]} ${match[2]}:${match[3]}:${match[4]}`;
    }

    return value;
}

function adcToVoltage(raw) {
    if (raw === null || raw === undefined || raw === "") return null;
    return (Number(raw) * 3.3 / 4095);
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

async function loadStatus() {
    try {
        const data = await getJSON("/api/status");
        const connection = document.getElementById("connection");

        if (!data.available) {
            setText("stm32Status", "DISCONNECTED");
            connection.innerHTML = '<span class="dot"></span>Chưa có dữ liệu';
            connection.classList.add("error");
            return;
        }

        const status = data.status;

        setText("stm32Status", status.connection || "DISCONNECTED");
        setText("adcStatus", status.adc_status || "UNKNOWN");
        setText("dacStatus", status.dac_status || "UNKNOWN");
        setText("serialStatus", status.serial_status || "IDLE");

        connection.innerHTML = '<span class="dot"></span>Dữ liệu sẵn sàng';
        connection.classList.remove("error");
    } catch (error) {
        console.error("loadStatus error:", error);

        const connection = document.getElementById("connection");
        connection.innerHTML = '<span class="dot"></span>Lỗi kết nối Web';
        connection.classList.add("error");
    }
}

async function loadMeasurements() {
    const tbody = document.getElementById("measurements");

    try {
        const data = await getJSON("/api/measurements?limit=20");
        const rows = data.measurements || [];

        if (rows.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty">Chưa có dữ liệu đo</td>
                </tr>
            `;
            setText("adc12", "-");
            setText("adc13", "-");
            setText("dac1", "-");
            setText("dac2", "-");
            setText("adc12Voltage", "- V");
            setText("adc13Voltage", "- V");
            return;
        }

        const latest = rows[0];

        setText("adc12", latest.adc12 ?? "-");
        setText("adc13", latest.adc13 ?? "-");
        setText("dac1", latest.dac1 ?? "-");
        setText("dac2", latest.dac2 ?? "-");

        const v12 = adcToVoltage(latest.adc12);
        const v13 = adcToVoltage(latest.adc13);

        setText("adc12Voltage", v12 === null ? "- V" : `${v12.toFixed(3)} V`);
        setText("adc13Voltage", v13 === null ? "- V" : `${v13.toFixed(3)} V`);
        setText("updated", "Cập nhật: " + formatTimestamp(latest.timestamp));

        tbody.innerHTML = rows.map(row => `
            <tr>
                <td>${formatTimestamp(row.timestamp)}</td>
                <td>${row.adc12 ?? "—"}</td>
                <td>${row.adc13 ?? "—"}</td>
                <td>${row.dac1 ?? "—"}</td>
                <td>${row.dac2 ?? "—"}</td>
                <td>${row.source ?? "—"}</td>
            </tr>
        `).join("");
    } catch (error) {
        console.error("loadMeasurements error:", error);

        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty">Không đọc được dữ liệu đo</td>
            </tr>
        `;
    }
}

async function loadEvents() {
    const tbody = document.getElementById("events");

    try {
        const data = await getJSON("/api/events?limit=20");
        const rows = data.events || [];

        if (rows.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty">Chưa có sự kiện</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = rows.map(row => `
            <tr>
                <td>${formatTimestamp(row.timestamp)}</td>
                <td><span class="event-badge">${row.event_type || "—"}</span></td>
                <td>${row.value ?? "—"}</td>
                <td>${row.detail ?? "—"}</td>
            </tr>
        `).join("");
    } catch (error) {
        console.error("loadEvents error:", error);

        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty">Không đọc được lịch sử</td>
            </tr>
        `;
    }
}

async function refresh() {
    await Promise.all([
        loadStatus(),
        loadMeasurements(),
        loadEvents(),
    ]);
}

refresh();
setInterval(refresh, 2000);
