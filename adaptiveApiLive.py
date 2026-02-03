import requests
from typing import List, Dict, Any, Optional, TypedDict
from enum import Enum
from datetime import datetime

# Enums
class Running(Enum):
    NOT_RUNNING = 0
    RUNNING_BUT_PAUSED = 1
    RUNNING_NOW = 2

class Mode(Enum):
    RUN = 0
    DEBUG = 1
    TEST = 2
    OVERRIDE = 3

# Type definitions based on apiLiveData.ts
class LiveMachine(TypedDict):
    machine: str
    type: Optional[str]

class DashboardEntry(TypedDict):
    name: str
    lastModified: int
    sizeInBytes: int

class ScreenButton(TypedDict):
    text: str
    svg: Optional[Dict[str, str]]  # {viewBox: str, d: str}

class TimelineItem(TypedDict):
    start: int
    end: int
    resource: str
    id: Any

class Job(TypedDict):
    id: Any
    running: Optional[Dict[str, int]]  # {currentStep: int, changingStep?: int}
    blocked: Optional[bool]
    committed: Optional[bool]
    foregroundColor: Optional[str]
    notes: Optional[str]
    programs: Optional[List[Any]]
    parameters: Optional[List[Dict[str, str]]]  # [{command: str}]
    profile: Optional[Dict[str, Any]]  # ValueProfile

class ScheduledJob(Job):
    start: int
    end: int
    standard: Optional[int]

class ProgramNumberAndName(TypedDict):
    number: str
    name: str

class Program(TypedDict):
    number: str
    name: Optional[str]
    steps: Any  # Step[] | number
    notes: Optional[str]
    code: Optional[str]
    modifiedTime: Optional[datetime]
    modifiedBy: Optional[str]

class ProgramGroup(TypedDict):
    group: str
    programs: List[Program]

class SampleStep(TypedDict):
    index: int
    # ... other Step properties

class RunningProfile(TypedDict):
    currentStep: int
    changingStep: int
    sampleSteps: List[SampleStep]
    # ... other ValueProfile properties

class ShiftPattern(TypedDict):
    fromDate: Optional[int]
    repeatPeriodInDays: Optional[int]
    startTime: int
    shifts: List['Shift']

class Shift(TypedDict):
    name: str
    duration: int

class GroupNumberAndName(TypedDict):
    group: Optional[str]
    number: str
    name: str

class Tag(TypedDict):
    # Based on common tag properties - you may need to adjust
    name: str
    type: Optional[str]
    value: Optional[Any]
    description: Optional[str]

class Command(TypedDict):
    # Based on common command properties - you may need to adjust
    name: str
    description: Optional[str]
    parameters: Optional[List[str]]

# Type aliases
LiveMachines = List[LiveMachine]
DashboardEntries = List[DashboardEntry]

class AdaptiveApiLive:
    def __init__(self, server: str, token: str):
        self.server = server 
        self.token = token
        
        # Using a Session for connection pooling and shared headers
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "AdaptiveApiLive/1.0"
        })

    def _url(self, path: str) -> str:
        return f"{self.server}/api/v1/live/{path.lstrip('/')}"

    def _fetch(self, path: str, query: Optional[dict] = None) -> Any:
        url = self._url(path)
        response = self.session.get(url, params=query, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_machines(self, machines: Optional[List[str]] = None) -> LiveMachines:
        """Fetch a list of machines. If 'machines' is provided, fetch only those."""
        return self._fetch("machines", {"m": machines} if machines else None)

    def fetch_tag_values_multiple(self, machines: List[str], tags: List[str]) -> Dict[str, List[Any]]:
        """Fetch values for the same tags from multiple machines."""
        return self._fetch("tagValues", {"m": machines, "t": tags})

    def fetch_tag_values(self, machine: str, tags: List[str]) -> List[Any]:
        """Fetch values for a single machine and extract the specific data."""
        data = self.fetch_tag_values_multiple([machine], tags)
        return data.get(machine, [])

    def fetch_tags_multiple(self, machines: List[str]) -> Dict[str, List[Tag]]:
        """Fetch tags for multiple machines."""
        return self._fetch("tags", {"m": machines})

    def fetch_tags(self, machine: str) -> List[Tag]:
        """Fetch tags for a single machine."""
        data = self.fetch_tags_multiple([machine])
        return data.get(machine, [])

    def fetch_commands_multiple(self, machines: List[str]) -> Dict[str, List[Command]]:
        """Fetch commands for multiple machines."""
        return self._fetch("commands", {"m": machines})

    def fetch_commands(self, machine: str) -> List[Command]:
        """Fetch commands for a single machine."""
        data = self.fetch_commands_multiple([machine])
        return data.get(machine, [])

    def fetch_dashboard_entries(self) -> DashboardEntries:
        """Fetch dashboard entries."""
        return self._fetch("dashboardEntries")

    def fetch_dashboard(self, name: str) -> Optional[bytes]:
        """Fetch a dashboard by name, returns binary data or None if not found."""
        url = self._url("dashboard")
        response = self.session.get(url, params={"name": name}, timeout=10)
        if response.status_code == 200:
            return response.content
        return None

    def fetch_scene(self, name: str) -> Optional[bytes]:
        """Fetch a scene by name, returns binary data or None if not found."""
        url = self._url("scene")
        response = self.session.get(url, params={"name": name}, timeout=10)
        if response.status_code == 200:
            return response.content
        return None

    def fetch_screen_buttons_multiple(self, machines: List[str]) -> Dict[str, List[ScreenButton]]:
        """Fetch screen buttons for multiple machines."""
        return self._fetch("screenButtons", {"m": machines})

    def fetch_screen_buttons(self, machine: str) -> List[ScreenButton]:
        """Fetch screen buttons for a single machine."""
        data = self.fetch_screen_buttons_multiple([machine])
        return data.get(machine, [])

    def fetch_program_groups_multiple(self, machines: List[str], group: Optional[str] = None, only_step_counts: bool = False) -> Dict[str, List[ProgramGroup]]:
        """Fetch program groups for multiple machines."""
        query = {"m": machines}
        if group is not None:
            query["group"] = group
        if only_step_counts:
            query["onlyStepCounts"] = "true"
        return self._fetch("programs", query)

    def fetch_program_groups(self, machine: str, group: Optional[str] = None, only_step_counts: bool = False) -> List[ProgramGroup]:
        """Fetch program groups for a single machine."""
        data = self.fetch_program_groups_multiple([machine], group, only_step_counts)
        return data.get(machine, [])

    def fetch_jobs_multiple(self, machines: List[str]) -> Dict[str, List[ScheduledJob]]:
        """Fetch scheduled jobs for multiple machines."""
        return self._fetch("jobs", {"m": machines})

    def fetch_jobs(self, machine: str) -> List[ScheduledJob]:
        """Fetch scheduled jobs for a single machine."""
        data = self.fetch_jobs_multiple([machine])
        return data.get(machine, [])

    def fetch_messages_multiple(self, machines: List[str]) -> Dict[str, List[str]]:
        """Fetch messages for multiple machines."""
        return self._fetch("messages", {"m": machines})

    def fetch_messages(self, machine: str) -> List[str]:
        """Fetch messages for a single machine."""
        data = self.fetch_messages_multiple([machine])
        return data.get(machine, [])

    def fetch_profiles(self, machines: List[str]) -> Dict[str, Optional[RunningProfile]]:
        """Fetch running profiles for multiple machines."""
        return self._fetch("profiles", {"m": machines})

    def fetch_screen_multiple(self, machines: List[str], page: Optional[int] = None) -> Dict[str, List[str]]:
        """Fetch screen data for multiple machines."""
        query = {"m": machines}
        if page is not None:
            query["page"] = page
        return self._fetch("screen", query)

    def fetch_screen(self, machine: str, page: Optional[int] = None) -> List[str]:
        """Fetch screen data for a single machine."""
        data = self.fetch_screen_multiple([machine], page)
        return data.get(machine, [])

    def url_command_icon(self, machine: str, command: str) -> str:
        """Generate URL for command icon."""
        return f"{self._url('commandIcon')}?m={machine}&c={command}"