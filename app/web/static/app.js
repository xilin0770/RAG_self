(function () {
  "use strict";

  const els = {
    apiBase: document.getElementById("api-base"),
    apiHint: document.getElementById("api-hint"),
    useOrigin: document.getElementById("use-origin"),
    importForm: document.getElementById("import-form"),
    importSubmit: document.getElementById("import-submit"),
    importSubmitOutput: document.getElementById("import-submit-output"),
    taskIdInput: document.getElementById("task-id-input"),
    queryTask: document.getElementById("query-task"),
    autoTask: document.getElementById("auto-task"),
    importStatusOutput: document.getElementById("import-status-output"),
    qaForm: document.getElementById("qa-form"),
    qaQuery: document.getElementById("qa-query"),
    qaStart: document.getElementById("qa-start"),
    qaStop: document.getElementById("qa-stop"),
    streamState: document.getElementById("stream-state"),
    streamAnswer: document.getElementById("stream-answer"),
    qaCitations: document.getElementById("qa-citations"),
  };

  const state = {
    taskTimer: null,
    activeTaskId: null,
    streamAbortController: null,
    streamBuffer: "",
    streamEnded: false,
  };

  function normalizeBase(value) {
    const trimmed = (value || "").trim();
    if (!trimmed) return window.location.origin;
    return trimmed.endsWith("/") ? trimmed.slice(0, -1) : trimmed;
  }

  function getBaseUrl() {
    const base = normalizeBase(els.apiBase.value);
    els.apiBase.value = base;
    return base;
  }

  function showBaseHint() {
    els.apiHint.textContent = `当前请求地址：${getBaseUrl()}`;
  }

  function pretty(value) {
    if (typeof value === "string") return value;
    try {
      return JSON.stringify(value, null, 2);
    } catch (_err) {
      return String(value);
    }
  }

  async function parseResponse(response) {
    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch (_err) {
      return text;
    }
  }

  function stopTaskPolling() {
    if (state.taskTimer) {
      window.clearInterval(state.taskTimer);
      state.taskTimer = null;
      els.autoTask.textContent = "自动轮询";
    }
  }

  function isTaskFinished(status) {
    return ["completed", "failed", "error", "done"].includes(String(status || "").toLowerCase());
  }

  async function queryTaskStatus(taskId) {
    const base = getBaseUrl();
    const response = await fetch(`${base}/import/${taskId}/status`);
    const data = await parseResponse(response);
    if (!response.ok) {
      throw new Error(typeof data === "string" ? data : pretty(data));
    }
    els.importStatusOutput.textContent = pretty(data);
    if (isTaskFinished(data.status)) {
      stopTaskPolling();
    }
    return data;
  }

  function startTaskPolling(taskId) {
    stopTaskPolling();
    state.activeTaskId = taskId;
    els.autoTask.textContent = "停止轮询";
    queryTaskStatus(taskId).catch((err) => {
      els.importStatusOutput.textContent = `查询失败：${err.message}`;
      stopTaskPolling();
    });

    state.taskTimer = window.setInterval(() => {
      queryTaskStatus(taskId).catch((err) => {
        els.importStatusOutput.textContent = `查询失败：${err.message}`;
        stopTaskPolling();
      });
    }, 2000);
  }

  function setStreamState(kind, text) {
    els.streamState.className = `badge ${kind}`;
    els.streamState.textContent = text;
  }

  function setStreamRunning(running) {
    els.qaStart.disabled = running;
    els.qaStop.disabled = !running;
    els.qaQuery.disabled = running;
  }

  function appendStreamText(text) {
    els.streamAnswer.textContent += text;
    els.streamAnswer.scrollTop = els.streamAnswer.scrollHeight;
  }

  function renderCitations(citations) {
    if (!Array.isArray(citations) || citations.length === 0) {
      els.qaCitations.className = "citations-empty";
      els.qaCitations.textContent = "暂无";
      return;
    }
    els.qaCitations.className = "";
    const html = citations
      .map((item) => {
        const meta = [
          `#${item.index ?? "-"}`,
          item.course_name ? `课程：${item.course_name}` : "",
          item.chapter_name ? `章节：${item.chapter_name}` : "",
          item.source_file ? `来源：${item.source_file}` : "",
        ]
          .filter(Boolean)
          .join(" | ");
        const content = item.content || "";
        return `<div class="citation-item"><div class="citation-meta">${escapeHtml(meta)}</div><div>${escapeHtml(content)}</div></div>`;
      })
      .join("");
    els.qaCitations.innerHTML = html;
  }

  function escapeHtml(raw) {
    return String(raw)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function handleSseEventPayload(payload) {
    if (!payload) return;

    if (payload === "[DONE]") {
      state.streamEnded = true;
      setStreamState("done", "已完成");
      return;
    }

    if (payload.startsWith("[ERROR]")) {
      setStreamState("error", "服务报错");
      appendStreamText(`\n\n[错误] ${payload.slice("[ERROR]".length)}`);
      return;
    }

    if (payload.startsWith("[CITATIONS]")) {
      const raw = payload.slice("[CITATIONS]".length);
      try {
        const citations = JSON.parse(raw);
        renderCitations(citations);
      } catch (_err) {
        renderCitations([]);
      }
      return;
    }

    appendStreamText(payload);
  }

  function consumeSseBuffer(force) {
    const separators = ["\r\n\r\n", "\n\n", "\r\r"];
    while (true) {
      let cut = -1;
      let sepLen = 0;

      for (const sep of separators) {
        const idx = state.streamBuffer.indexOf(sep);
        if (idx !== -1 && (cut === -1 || idx < cut)) {
          cut = idx;
          sepLen = sep.length;
        }
      }

      if (cut === -1) break;
      const eventBlock = state.streamBuffer.slice(0, cut);
      state.streamBuffer = state.streamBuffer.slice(cut + sepLen);

      const dataLines = eventBlock
        .split(/\r?\n/)
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trimStart());

      if (dataLines.length > 0) {
        handleSseEventPayload(dataLines.join("\n"));
      }
    }

    if (force && state.streamBuffer.trim()) {
      const dataLines = state.streamBuffer
        .split(/\r?\n/)
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trimStart());
      if (dataLines.length > 0) {
        handleSseEventPayload(dataLines.join("\n"));
      }
      state.streamBuffer = "";
    }
  }

  async function streamAnswer(query) {
    const base = getBaseUrl();
    state.streamAbortController = new AbortController();
    state.streamBuffer = "";
    state.streamEnded = false;

    setStreamRunning(true);
    setStreamState("streaming", "流式输出中");
    els.streamAnswer.textContent = "";
    renderCitations([]);

    const response = await fetch(`${base}/qa/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      signal: state.streamAbortController.signal,
    });

    if (!response.ok) {
      const errPayload = await parseResponse(response);
      throw new Error(typeof errPayload === "string" ? errPayload : pretty(errPayload));
    }

    if (!response.body) {
      throw new Error("浏览器不支持流式读取（response.body 为空）");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        state.streamBuffer += decoder.decode(value, { stream: true });
        consumeSseBuffer(false);
      }
      state.streamBuffer += decoder.decode();
      consumeSseBuffer(true);
    } finally {
      reader.releaseLock();
    }

    if (!state.streamEnded) {
      setStreamState("done", "流结束");
    }
  }

  els.useOrigin.addEventListener("click", () => {
    els.apiBase.value = window.location.origin;
    showBaseHint();
  });

  els.apiBase.addEventListener("change", showBaseHint);
  els.apiBase.addEventListener("blur", showBaseHint);

  els.importForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const base = getBaseUrl();
    const formData = new FormData(els.importForm);
    els.importSubmit.disabled = true;

    try {
      const response = await fetch(`${base}/import`, {
        method: "POST",
        body: formData,
      });
      const data = await parseResponse(response);
      if (!response.ok) {
        throw new Error(typeof data === "string" ? data : pretty(data));
      }
      els.importSubmitOutput.textContent = pretty(data);
      if (data.task_id) {
        els.taskIdInput.value = String(data.task_id);
        startTaskPolling(data.task_id);
      }
    } catch (err) {
      els.importSubmitOutput.textContent = `导入提交失败：${err.message}`;
    } finally {
      els.importSubmit.disabled = false;
    }
  });

  els.queryTask.addEventListener("click", async () => {
    const taskId = Number(els.taskIdInput.value);
    if (!taskId) {
      els.importStatusOutput.textContent = "请先填写有效的任务 ID";
      return;
    }
    try {
      await queryTaskStatus(taskId);
    } catch (err) {
      els.importStatusOutput.textContent = `查询失败：${err.message}`;
    }
  });

  els.autoTask.addEventListener("click", () => {
    const taskId = Number(els.taskIdInput.value || state.activeTaskId);
    if (!taskId) {
      els.importStatusOutput.textContent = "请先填写有效的任务 ID";
      return;
    }
    if (state.taskTimer) {
      stopTaskPolling();
      return;
    }
    startTaskPolling(taskId);
  });

  els.qaForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = els.qaQuery.value.trim();
    if (!query) return;

    try {
      await streamAnswer(query);
    } catch (err) {
      if (err.name === "AbortError") {
        setStreamState("idle", "已停止");
      } else {
        setStreamState("error", "流式失败");
        appendStreamText(`\n\n[错误] ${err.message}`);
      }
    } finally {
      setStreamRunning(false);
      state.streamAbortController = null;
    }
  });

  els.qaStop.addEventListener("click", () => {
    if (state.streamAbortController) {
      state.streamAbortController.abort();
    }
  });

  els.apiBase.value = window.location.origin;
  showBaseHint();
  setStreamState("idle", "空闲");
})();
